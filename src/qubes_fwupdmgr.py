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
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from distutils.version import LooseVersion as l_ver

FWUPD_QUBES_DIR = "/usr/share/fwupd-qubes"
FWUPD_DOM0_UPDATE = os.path.join(FWUPD_QUBES_DIR, "src/fwupd-dom0-update")
FWUPD_DOM0_DIR = "/root/.cache/fwupd"
FWUPD_DOM0_METADATA_DIR = os.path.join(FWUPD_DOM0_DIR, "metadata")
FWUPD_DOM0_UPDATES_DIR = os.path.join(FWUPD_DOM0_DIR, "updates")
FWUPD_USBVM_LOG = os.path.join(FWUPD_DOM0_DIR, "usbvm-devices.log")
FWUPD_DOM0_METADATA_SIGNATURE = os.path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_DOM0_METADATA_FILE = os.path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz"
)
FWUPD_DOWNLOAD_PREFIX = "https://fwupd.org/downloads/"
FWUPDMGR = "/bin/fwupdmgr"

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
            "update": "Updates chosen device to latest firmware version",
            "downgrade": "Downgrade chosen device to chosen firmware version",
            "clean": "Deletes all cached update files"
        }
    ],
    "Help": [
        {
            "-h --help": "Show help options"
        }
    ]
}

EXIT_CODES = {
    "ERROR": 1,
    "SUCCESS": 0,
    "NO_UPDATES": 99,
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
            raise Exception("Metadata signature does not exist")

    def refresh_metadata(self):
        """Updates metadata with downloaded files."""
        self._download_metadata()
        cmd_refresh = [
            FWUPDMGR,
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
        print(self.output)
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Refresh failed")
        if not METADATA_REFRESH_REGEX.match(self.output):
            raise Exception("Metadata signature does not exist")

    def _get_dom0_updates(self):
        """Gathers infromations about available updates."""
        cmd_get_dom0_updates = [
            "/bin/fwupdagent",
            "get-updates"
        ]
        p = subprocess.Popen(
            cmd_get_dom0_updates,
            stdout=subprocess.PIPE
        )
        self.dom0_updates_info = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting available updates failed")

    def _parse_dom0_updates_info(self, updates_info):
        """Creates dictionary and list with informations about updates.

        Keywords argument:
        updates_info - gathered update informations
        """
        self.dom0_updates_info_dict = json.loads(updates_info)
        self.dom0_updates_list = [
            {
                    "Name": device["Name"],
                    "Version": device["Version"],
                    "Releases": [
                        {
                            "Version": update["Version"],
                            "Url": update["Uri"],
                            "Checksum": update["Checksum"][0],
                            "Description": update["Description"]
                        } for update in device["Releases"]
                    ]
            } for device in self.dom0_updates_info_dict["Devices"]
        ]

    def _download_firmware_updates(self, url, sha):
        """Initializes downloading firmware upadate archive.

        Keywords arguments:
        url -- url path to the firmware upadate archive
        sha -- SHA1 checksum of the firmware update archive
        """
        name = url.replace(FWUPD_DOWNLOAD_PREFIX, "")
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
            raise Exception("Firmware update files do not exist")

    def _user_input(self, updates_list, downgrade=False):
        """UI for update process.

        Keywords arguments:
        updates_list - list of updates for specified device
        downgrade -- downgrade flag
        """
        decorator = "======================================================"
        if len(updates_list) == 0:
            print("No updates available.")
            return EXIT_CODES["NO_UPDATES"]
        if downgrade:
            print("Available downgrades:")
        else:
            print("Available updates:")
        print(decorator)
        for i, device in enumerate(updates_list):
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print("%s. Device: %s" % (i+1, device["Name"]))
            print("   Current firmware version:\t %s" % device["Version"])
            for update in device["Releases"]:
                print(decorator)
                print("   Firmware update version:\t %s" % update["Version"])
                description = update["Description"].replace("<p>", "")
                description = description.replace("<li>", "")
                description = description.replace("<ul>", "")
                description = description.replace("</ul>", "")
                description = description.replace("</p>", "\n   ")
                description = description.replace("</li>", "\n   ")
                print("   Description: %s" % description)
            print(decorator)

        while True:
            try:
                print("If you want to abandon process press 'N'.")
                choice = input(
                    "Otherwise choose a device number: "
                )
                if choice == 'N' or choice == 'n':
                    return EXIT_CODES["NO_UPDATES"]
                device_number = int(choice)-1
                if 0 <= device_number < len(updates_list):
                    if not downgrade:
                        return device_number
                    break
                else:
                    raise ValueError()
            except ValueError:
                print("Invalid choice.")

        if downgrade:
            while True:
                try:
                    releases = updates_list[device_number]["Releases"]
                    for i, fw_dngd in enumerate(releases):
                        print(decorator)
                        print(
                            "  %s. Firmware downgrade version:\t %s" %
                            (i+1, fw_dngd["Version"])
                        )
                        description = fw_dngd["Description"].replace("<p>", "")
                        description = description.replace("<li>", "")
                        description = description.replace("<ul>", "")
                        description = description.replace("</ul>", "")
                        description = description.replace("</p>", "\n   ")
                        description = description.replace("</li>", "\n   ")
                        print("   Description: %s" % description)
                    print("If you want to abandon downgrade process press N.")
                    choice = input(
                        "Otherwise choose downgrade number: "
                    )
                    if choice == 'N' or choice == 'n':
                        return EXIT_CODES["NO_UPDATES"]
                    downgrade_number = int(choice)-1
                    if 0 <= downgrade_number < len(releases):
                        return device_number, downgrade_number
                    else:
                        raise ValueError()
                except ValueError:
                    print("Invalid choice.")

    def _parse_parameters(self, updates_list, choice):
        """Parses device name, url, version and SHA1 checksum of the file list.

        Keywords arguments:
        updates_list - list of updates for specified device
        choice -- number of device to be updated
        """
        self.name = updates_list[choice]["Name"]
        self.version = updates_list[choice]["Releases"][0]["Version"]
        for ver_check in updates_list[choice]["Releases"]:
            if l_ver(ver_check["Version"]) >= l_ver(self.version):
                self.version = ver_check["Version"]
                self.url = ver_check["Url"]
                self.sha = ver_check["Checksum"]

    def _install_firmware_update(self, path):
        """Installs firmware update for specified device.

        Keywords arguments:
        path - absolute path to firmware update archive
        """
        cmd_install = [
            FWUPDMGR,
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
        path -- absolute path of the updates files
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
            if l_ver(metainfo_ver) < l_ver(dmi_ver):
                raise ValueError(
                    "%s < %s Downgrade not allowed" %
                    (
                        metainfo_ver,
                        dmi_ver
                    )
                )

    def _get_dom0_devices(self):
        """Gathers informations about devices connected in dom0."""
        cmd_get_dom0_devices = [
            "/bin/fwupdagent",
            "get-devices"
        ]
        p = subprocess.Popen(
            cmd_get_dom0_devices,
            stdout=subprocess.PIPE
        )
        self.dom0_devices_info = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting devices info failed")

    def _get_usbvm_devices(self):
        """Gathers informations about devices connected in sys-usb."""
        if os.path.exists(FWUPD_USBVM_LOG):
            os.remove(FWUPD_USBVM_LOG)
        usbvm_cmd = '"/usr/libexec/fwupd/fwupdagent get-devices"'
        cmd_get_usbvm_devices = 'qvm-run --nogui --pass-io sys-usb %s > %s' % (
            usbvm_cmd,
            FWUPD_USBVM_LOG
        )
        p = subprocess.Popen(
            cmd_get_usbvm_devices,
            shell=True
        )
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting sys-usb devices info failed")
        if not os.path.exists(FWUPD_USBVM_LOG):
            raise Exception("sys-usb device info log does not exist")

    def _parse_usbvm_updates(self, usbvm_devices_info):
        """Creates dictionary and list with informations about updates.

        Keywords argument:
        usbvm_devices_info - gathered usbvm informations
        """
        self.usbvm_updates_list = []
        usbvm_device_info_dict = json.loads(usbvm_devices_info)
        for device in usbvm_device_info_dict["Devices"]:
            if "Releases" in device:
                self.usbvm_updates_list.append(
                    {
                        "Name": device["Name"],
                        "Version": device["Version"],
                        "Releases": []
                    }
                )
                current_version = device["Version"]
                for update in device["Releases"]:
                    if l_ver(update["Version"]) > current_version:
                        self.usbvm_updates_list[-1]["Releases"].append(
                            {
                                "Version": update["Version"],
                                "Url": update["Uri"],
                                "Checksum": update["Checksum"][0],
                                "Description": update["Description"]
                            }
                        )

    def update_firmware(self):
        """Updates firmware of the specified device."""
        self._get_dom0_updates()
        self._parse_dom0_updates_info(self.dom0_updates_info)
        choice = self._user_input(self.dom0_updates_list)
        if choice == EXIT_CODES["NO_UPDATES"]:
            exit(EXIT_CODES["NO_UPDATES"])
        self._parse_parameters(self.dom0_updates_list, choice)
        self._download_firmware_updates(self.url, self.sha)
        arch_name = self.url.replace(FWUPD_DOWNLOAD_PREFIX, "")
        arch_path = os.path.join(FWUPD_DOM0_UPDATES_DIR, arch_name)
        if self.name == "System Firmware":
            path = arch_path.replace(".cab", "")
            self._verify_dmi(path, self.version)
        self._install_firmware_update(arch_path)

    def _parse_dom0_downgrades(self, device_list):
        """Parses informations about possible downgrades

         Keywords argument:
        device_list -- list of connected devices
        """
        self.downgrades = []
        dom0_devices_info_dict = json.loads(device_list)
        for device in dom0_devices_info_dict["Devices"]:
            if "Releases" in device:
                version = device["Version"]
                self.downgrades.append(
                    {
                        "Name": device["Name"],
                        "Version": device["Version"],
                        "Releases": [
                            {
                                "Version": downgrade["Version"],
                                "Description": downgrade["Description"],
                                "Url": downgrade["Uri"],
                                "Checksum": downgrade["Checksum"][0]
                            } for downgrade in device["Releases"]
                            if l_ver(downgrade["Version"]) < l_ver(version)
                        ]
                    }
                )

    def _install_firmware_downgrade(self, path):
        """Installs firmware downgrade for specified device.

        Keywords arguments:
        path - absolute path to firmware downgrade archive
        """
        cmd_install = [
            FWUPDMGR,
            "--allow-older",
            "install",
            path
        ]
        p = subprocess.Popen(cmd_install)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware downgrade failed")

    def downgrade_firmware(self):
        """Downgrades firmware of the specified device."""
        self._get_dom0_devices()
        self._parse_dom0_downgrades(self.dom0_devices_info)
        if self.downgrades:
            ret_input = self._user_input(self.downgrades, downgrade=True)
            if ret_input == EXIT_CODES["NO_UPDATES"]:
                exit(EXIT_CODES["NO_UPDATES"])
            device_choice, downgrade_choice = ret_input
            releases = self.downgrades[device_choice]["Releases"]
            downgrade_url = releases[downgrade_choice]["Url"]
            downgrade_sha = releases[downgrade_choice]["Checksum"]
            self._download_firmware_updates(
                downgrade_url,
                downgrade_sha
            )
            arch_name = downgrade_url.replace(
                FWUPD_DOWNLOAD_PREFIX,
                ""
            )
            arch_path = os.path.join(FWUPD_DOM0_UPDATES_DIR, arch_name)
            if self.downgrades[device_choice]["Name"] == "System Firmware":
                path = arch_path.replace(".cab", "")
                self._verify_dmi(
                    path,
                    self.downgrades[device_choice]["Version"],
                    downgrade=True
                )
            self._install_firmware_downgrade(arch_path)
        else:
            print("No downgrades avaible")

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

    def _updates_crawler(self, updates_list, adminVM=True):
        """Prints updates informations for dom0 and sys-usb

        Keywords arguments:
        updates_list -- list of devices updates
        adminVM -- dom0 flag
        """
        decorator = "======================================================"
        if adminVM:
            print("Dom0 updates:")
        else:
            print("sys-usb updates:")
        print(decorator)
        if len(updates_list) == 0:
            print("No updates available.")
            return EXIT_CODES["NO_UPDATES"]
        else:
            print("Available updates:")
            print(decorator)
            for i, device in enumerate(updates_list):
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                print("%s. Device: %s" % (i+1, device["Name"]))
                print("   Current firmware version:\t %s" % device["Version"])
                for update in device["Releases"]:
                    print(decorator)
                    print(
                        "   Firmware update "
                        "version:\t %s" % update["Version"]
                    )
                    print("   URL:\t %s" % update["Url"])
                    print("   SHA1 checksum:\t %s" % update["Checksum"])
                    description = update["Description"].replace("<p>", "")
                    description = description.replace("<li>", "")
                    description = description.replace("<ul>", "")
                    description = description.replace("</ul>", "")
                    description = description.replace("</p>", "\n   ")
                    description = description.replace("</li>", "\n   ")
                    print("   Description: %s" % description)
                print(decorator)

    def get_devices_qubes(self):
        """Gathers and prints devices information."""
        self._get_dom0_devices()
        self._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            usbvm_device_info_dict = json.loads(usbvm_device_info.read())
        dom0_devices_info_dict = json.loads(self.dom0_devices_info)
        self._output_crawler(dom0_devices_info_dict, 0)
        self._output_crawler(usbvm_device_info_dict, 0)

    def get_updates_qubes(self):
        """Gathers and prints updates information."""
        self._get_dom0_updates()
        self._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            usbvm_device_info_dict = json.loads(usbvm_device_info.read())
        self._parse_usbvm_updates(usbvm_device_info_dict)
        self._parse_dom0_updates_info(self.dom0_updates_info)
        self._updates_crawler(self.dom0_updates_list)
        self._updates_crawler(self.usbvm_updates_list, adminVM=False)

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
        exit(EXIT_CODES["ERROR"])
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
    elif sys.argv[1] == "downgrade":
        q.downgrade_firmware()
    elif sys.argv[1] == "clean":
        q.clean_cache()
    else:
        q.help()


if __name__ == '__main__':
    main()
