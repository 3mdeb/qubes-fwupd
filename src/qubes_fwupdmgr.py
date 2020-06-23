#!/usr/bin/python3
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2020  Norbert Kaminski  <norbert.kaminski@3mdeb.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#
import distutils.version as ver
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

FWUPD_QUBES_DIR = "/usr/share/fwupd-qubes"
FWUPD_DOM0_UPDATE = os.path.join(FWUPD_QUBES_DIR, "src/fwupd-dom0-update")
FWUPD_DOM0_DIR = "/root/.cache/fwupd"
FWUPD_DOM0_METADATA_DIR = os.path.join(FWUPD_DOM0_DIR, "metadata")
FWUPD_DOM0_UPDATES_DIR = os.path.join(FWUPD_DOM0_DIR, "updates")
FWUPD_DOM0_METADATA_SIGNATURE = os.path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_DOM0_METADATA_FILE = os.path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz"
)

METADATA_REFRESH_REGEX = re.compile(
    r"^Successfully refreshed metadata manually$"
)

HELP = {
    "Usage": [
        {
            "qubes-fwupd [OPTION…]": "\n",
            "get-devices": "Get all devices that support firmware updates",
            "get-updates": "Gets the list of updates for connected hardware",
            "refresh": "Refresh metadata from remote server",
            "update": "Updates all firmware to latest versions available",
            "clean": "Deletes all cached update files"
        }
    ],
    "Help": [
        {
            "-h --help": "Show help options"
        }
    ]
}


class QubesFwupdmgr:
    def _download_metadata(self):
        """Initialize downloading metadata files."""
        cmd_metadata = [
            FWUPD_DOM0_UPDATE,
            "--metadata"
        ]
        p = subprocess.Popen(cmd_metadata)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Metadata update failed")
        if not os.path.exists(FWUPD_DOM0_METADATA_FILE):
            raise ValueError("Metadata signature does not exist")

    def refresh_metadata(self):
        """Updates metadata with downloaded files."""
        self._download_metadata()
        cmd_refresh = [
            "/bin/fwupdmgr",
            "refresh",
            FWUPD_DOM0_METADATA_FILE,
            FWUPD_DOM0_METADATA_SIGNATURE,
            "lvfs"
        ]
        p = subprocess.Popen(
            cmd_refresh,
            stdout=subprocess.PIPE
        )
        self.output = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Refresh failed")
        if not METADATA_REFRESH_REGEX.match(self.output):
            raise ValueError("Metadata signature does not exist")

    def _get_updates(self):
        """Gathers infromations about available updates."""
        cmd_get_updates = [
            "/bin/fwupdagent",
            "get-updates"
        ]
        p = subprocess.Popen(
            cmd_get_updates,
            stdout=subprocess.PIPE
        )
        self.updates_info = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting available updates failed")

    def _parse_updates_info(self, updates_info):
        """Creates dictionary and list with informations about updates.

        Keywords argument:
        updates_info - gathered update informations
        """
        self.updates_info_dict = json.loads(updates_info)
        self.updates_list = [
            [
                device["Name"],
                device["Version"],
                [
                    [
                        update["Version"],
                        update["Uri"],
                        update["Checksum"][0]
                    ] for update in device["Releases"]
                ]
            ] for device in self.updates_info_dict["Devices"]
        ]

    def _download_firmware_updates(self, url, sha):
        """Initializes downloading firmware upadate archive.

        Keywords arguments:
        url -- url path to firmware upadate archive
        sha -- SHA1 checksum of the firmware update archive
        """
        name = url.replace("https://fwupd.org/downloads/", "")
        update_path = os.path.join(
            FWUPD_DOM0_UPDATES_DIR,
            name.replace(".cab", "")
        )
        cmd_fwdownload = [
            FWUPD_DOM0_UPDATE,
            "--update",
            "--url=%s" % url,
            "--sha=%s" % sha
        ]
        p = subprocess.Popen(cmd_fwdownload)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware download failed")
        if not os.path.exists(update_path):
            raise ValueError("Firmware update files do not exist")

    def _user_input(self, updates_list):
        """UI for update process.

        Keywords arguments:
        updates_list - list of updates for specified device
        """
        if len(updates_list) == 0:
            print("No updates available.")
            return 99

        print("Available updates:")
        print("======================================================")
        for i, device in enumerate(updates_list):
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print("%s. Device: %s" % (i+1, device[0]))
            print("   Current firmware version:\t %s" % device[1])
            for i, update in enumerate(device[2]):
                print("======================================================")
                print("   Firmware update version:\t %s" % update[0])
                print("   SHA1: %s" % update[2])
            print("======================================================")

        while(True):
            try:
                print("If you want to abandon update press 'N'.")
                choice = input(
                    "If you want to update a device, choose the number: "
                )
                if choice == 'N' or choice == 'n':
                    return 99
                device_number = int(choice)
                if 0 < device_number <= len(updates_list):
                    return device_number-1
                else:
                    raise ValueError()
            except ValueError:
                print("Invalid choice.")

    def _parse_parameters(self, updates_list, choice):
        """Parses device name, url, version and SHA1 checksum of the file list.

        Keywords arguments:
        updates_list - list of updates for specified device
        choice -- number of the device to be updated
        """
        self.name = updates_list[choice][0]
        self.version = updates_list[choice][2][0][0]
        for ver_check in updates_list[choice][2]:
            if ver.LooseVersion(ver_check[0]) >= ver.LooseVersion(self.version):
                self.version = ver_check[0]
                self.url = ver_check[1]
                self.sha = ver_check[2]

    def _install_firmware_update(self, path):
        """Installs firmware update for specified device.

        Keywords arguments:
        path - absolute path to firmware update path
        """
        cmd_install = [
            "/bin/fwupdmgr",
            "install",
            path
        ]
        p = subprocess.Popen(cmd_install)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware update failed")

    def _read_dmi(self):
        """Reads BIOS information from DMI."""
        cmd_dmidecode = [
            "dmidecode",
            "-t",
            "bios"
        ]
        p = subprocess.Popen(cmd_dmidecode, stdout=subprocess.PIPE)
        p.wait()
        if p.returncode != 0:
            raise Exception("dmidecode: Reading DMI failed")
        return p.communicate()[0].decode()

    def _verify_dmi(self, path, version, downgrade=False):
        """Verifies DMI tables for BIOS updates.

        Keywords arguments:
        path -- updates file absolute path
        version -- version of the update
        downgrade -- downgrade flag
        """
        dmi_info = self._read_dmi()
        path_metainfo = os.path.join(path, "firmware.metainfo.xml")
        tree = ET.parse(path_metainfo)
        root = tree.getroot()
        vendor = root.find("developer_name").text
        if vendor is None:
            raise ValueError("No vendor information in firmware metainfo.")
        if vendor not in dmi_info:
            raise ValueError("Wrong firmware provider.")
        metainfo_ver = root.find("releases").find("release").attrib['version']
        if version != metainfo_ver:
            raise ValueError("Wrong firmware version.")
        # Parsing version from dmidecode output
        for line in dmi_info.split("\n"):
            if 'Version: ' in line:
                dmi_ver = line.split(': ')[1]
        if not downgrade:
            if ver.LooseVersion(metainfo_ver) < ver.LooseVersion(dmi_ver):
                raise ValueError(
                    "%s < %s Downgrade not allowed" %
                    (
                        metainfo_ver,
                        dmi_ver
                    )
                )

    def _get_devices(self):
        """Gathers infromations about connected devices."""
        cmd_get_devices = [
            "/bin/fwupdagent",
            "get-devices"
        ]
        p = subprocess.Popen(
            cmd_get_devices,
            stdout=subprocess.PIPE
        )
        self.devices_info = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting devices info failed")

    def update_firmware(self):
        "Handles firmware update process."
        self._get_updates()
        self._parse_updates_info(self.updates_info)
        choice = self._user_input(self.updates_list)
        if choice == 99:
            exit(0)
        self._parse_parameters(self.updates_list, choice)
        self._download_firmware_updates(self.url, self.sha)
        name = self.url.replace("https://fwupd.org/downloads/", "")
        arch_path = os.path.join(FWUPD_DOM0_UPDATES_DIR, name)
        if self.name == "System Firmware":
            path = arch_path.replace(".cab", "")
            self._verify_dmi(path, self.version)
        self._install_firmware_update(arch_path)

    def _output_crawler(self, updev_dict, level):
        """Prints device and updates informations as a tree.

        Keywords arguments:
        updev_dict -- update/device information dictionary
        level -- level of the tree
        """
        def _tabs(key_word):
            return key_word + '\t'*(3 - int(len(key_word)/8))
        for updev_key in updev_dict:
            style = '\t'*level
            output = style + _tabs(updev_key + ":")
            if isinstance(updev_dict[updev_key], str):
                print(output + updev_dict[updev_key])
            elif isinstance(updev_dict[updev_key], int):
                print(output + str(updev_dict[updev_key]))
            elif isinstance(updev_dict[updev_key][0], str):
                for data in updev_dict[updev_key]:
                    print(output + data)
            elif isinstance(updev_dict[updev_key][0], dict):
                print(output)
                for nested_dict in updev_dict[updev_key]:
                    self._output_crawler(nested_dict, level+1)

    def get_devices_qubes(self):
        """Gathers and prints devices information."""
        self._get_devices()
        devices_info_dict = json.loads(self.devices_info)
        self._output_crawler(devices_info_dict, 0)

    def get_updates_qubes(self):
        """Gathers and prints updates information."""
        self._get_updates()
        self._parse_updates_info(self.updates_info)
        self._output_crawler(self.updates_info_dict, 0)

    def clean_cache(self):
        """Removes updates data"""
        print("Cleaning cache directories")
        if os.path.exists(FWUPD_DOM0_METADATA_DIR):
            shutil.rmtree(FWUPD_DOM0_METADATA_DIR)
        if os.path.exists(FWUPD_DOM0_UPDATES_DIR):
            shutil.rmtree(FWUPD_DOM0_UPDATES_DIR)

    def help(self):
        """Prints help informations"""
        self._output_crawler(HELP, 0)


def main():
    if os.geteuid() != 0:
        print("You need to have root privileges to run this script.\n")
        exit(1)
    q = QubesFwupdmgr()
    if len(sys.argv) < 2:
        q.help()
    elif sys.argv[1] == "get-updates":
        q.get_updates_qubes()
    elif sys.argv[1] == "get-devices":
        q.get_devices_qubes()
    elif sys.argv[1] == "refresh":
        q.refresh_metadata()
    elif sys.argv[1] == "update":
        q.update_firmware()
    elif sys.argv[1] == "clean":
        q.clean_cache()
    else:
        q.help()


if __name__ == '__main__':
    main()
