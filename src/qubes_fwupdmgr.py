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

FWUPD_QUBES_DIR = "/usr/share/fwupd-qubes"
FWUPD_DOM0_UPDATE = FWUPD_QUBES_DIR + "/src/fwupd-dom0-update"
FWUPD_DOM0_DIR = "/root/.cache/fwupd/"
FWUPD_DOM0_METADATA_DIR = FWUPD_DOM0_DIR + "metadata/"
FWUPD_DOM0_METADATA_SIGNATURE = FWUPD_DOM0_METADATA_DIR + "firmware.xml.gz.asc"
FWUPD_DOM0_METADATA_FILE = FWUPD_DOM0_METADATA_DIR + "firmware.xml.gz"
FWUPD_DOM0_UPDATES_DIR = FWUPD_DOM0_DIR + "updates/"

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
        name = url.replace("https://fwupd.org/downloads/", "")
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
        if not os.path.exists(FWUPD_DOM0_UPDATES_DIR + name[:-4]):
            raise ValueError("Firmware update files do not exist")

    def _user_input(self, updates_list):
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
        self.url = [url[1] for url in updates_list[choice][2]]
        self.sha = [sha[2] for sha in updates_list[choice][2]]

    def _install_firmware_update(self, path):
        cmd_install = [
            "/bin/fwudpmgr",
            "install",
            path
        ]
        p = subprocess.Popen(
            cmd_install,
            stdout=subprocess.STDOUT,
            stderr=subprocess.STDOUT
        )
        p.communicate()[0].decode("ascii")
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware update failed")

    def _verify_dmi(self):
        pass

    def _get_devices(self):
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
        self._get_updates()
        self._parse_updates_info(self.updates_info)
        choice = self._user_input(self.updates_list)
        if choice == 99:
            exit(0)
        self._parse_parameters(self.updates_list, choice)
        for i, url in enumerate(self.url):
            self._download_firmware_updates(url, self.sha[i])
            self._verify_dmi()
            name = url.replace("https://fwupd.org/downloads/", "")
            path = FWUPD_DOM0_UPDATES_DIR + name
            self._install_firmware_update(path)

    def _output_crawler(self, updev_dict, level):
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
        self._get_devices()
        devices_info_dict = json.loads(self.devices_info)
        self._output_crawler(devices_info_dict, 0)

    def get_updates_qubes(self):
        self._get_updates()
        self._parse_updates_info(self.updates_info)
        self._output_crawler(self.updates_info_dict, 0)

    def clean_cache(self):
        print("Cleaning cache directories")
        if os.path.exists(FWUPD_DOM0_METADATA_DIR):
            shutil.rmtree(FWUPD_DOM0_METADATA_DIR)
        if os.path.exists(FWUPD_DOM0_UPDATES_DIR):
            shutil.rmtree(FWUPD_DOM0_UPDATES_DIR)

    def help(self):
        self._output_crawler(HELP, 0)


def main():
    q = QubesFwupdmgr()
    if sys.argv[1] == "get-updates":
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
