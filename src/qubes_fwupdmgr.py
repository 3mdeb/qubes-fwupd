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
import subprocess
import sys

FWUPD_QUBES_DIR = "/usr/share/fwupd-qubes"
FWUPD_DOM0_UPDATE = FWUPD_QUBES_DIR + "/scripts/fwupd-dom0-update"
FWUPD_DOM0_DIR = "/root/.cache/fwupd/"
FWUPD_DOM0_METADATA_DIR = FWUPD_DOM0_DIR + "metadata/"
FWUPD_DOM0_METADATA_SIGNATURE = FWUPD_DOM0_METADATA_DIR + "firmware.xml.gz.asc"
FWUPD_DOM0_METADATA_FILE = FWUPD_DOM0_METADATA_DIR + "firmware.xml.gz"
FWUPD_DOM0_UPDATES_DIR = FWUPD_DOM0_DIR + "updates/"

METADATA_REFRESH_REGEX = re.compile(
    r"^Successfully refreshed metadata manually$"
)


class QubesFwupdmgr:
    def download_metadata(self):
        cmd_metadata = [
                        FWUPD_DOM0_UPDATE,
                        "--metadata"
                       ]
        p = subprocess.Popen(
                            cmd_metadata,
                            stdout=subprocess.STDOUT,
                            stderr=subprocess.STDOUT
                            )
        p.communicate()[0].decode("ascii")
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Metadata update failed")
        if os.path.exists(FWUPD_DOM0_METADATA_FILE):
            raise ValueError("Metadata signature does not exist")

    def refresh_metadata(self):
        self.download_metadata()
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
        if METADATA_REFRESH_REGEX.match(self.output):
            raise ValueError("Metadata signature does not exist")

    def get_updates(self):
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
        if METADATA_REFRESH_REGEX.match(self.output):
            raise ValueError("Metadata signature does not exist")

    def parse_updates_info(self, updates_info):
        """
        Method inits download process for update files.
        """
        self.updates_info_dict = json.loads(updates_info)
        print(self.updates_info_dict)
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

    def download_firmware_updates(self, url, sha):
        """
        Init update download process with `url` and `sha`.
        """
        name = url - "https://fwupd.org/downloads/"
        cmd_fwdownload = [
                        FWUPD_DOM0_UPDATE,
                        "--update",
                        "--url=%s" % url,
                        "--sha=%s" % sha
                       ]
        p = subprocess.Popen(
                            cmd_fwdownload,
                            stdout=subprocess.STDOUT,
                            stderr=subprocess.STDOUT
                            )
        p.communicate()[0].decode("ascii")
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware download failed")
        if os.path.exists(FWUPD_DOM0_UPDATES_DIR + name[:-4]):
            raise ValueError("Firmware update files do not exist")

    def user_input(self, updates_list):
        """
        Update process UI.
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

    def parse_parameters(self, updates_list, choice):
        self.url = [url[1] for url in updates_list[choice][2]]
        self.sha = [sha[2] for sha in updates_list[choice][2]]

    def install_firmware_update(self, path):
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

    def verify_dmi(self):
        pass

    def get_devices(self):
        self.devices_info = ""

    def update_firmware(self):
        self.get_updates()
        self.parse_updates_info(self.updates_info)
        choice = self.user_input(self.updates_list)
        if choice == 99:
            exit(0)
        self.parse_parameters(self.updates_list, choice)
        for i, url in enumerate(self.url):
            self.download_firmware_updates(url, self.sha[i])
            self.verify_dmi()
            name = url.replace("https://fwupd.org/downloads/", "")
            path = FWUPD_DOM0_UPDATES_DIR + name
            self.install_firmware_update(path)

    def output_crawler(self, updev_dict, level):
        """
        Prints nested dictionries
        """
        def tabs(key_word): return key_word + '\t'*(3 - int(len(key_word)/8))
        for updev_key in updev_dict:
            style = '\t'*level
            output = style + tabs(updev_key + ":")
            if isinstance(updev_dict[updev_key], str):
                output = output + updev_dict[updev_key]
                print(output)
            elif isinstance(updev_dict[updev_key], int):
                output = output + str(updev_dict[updev_key])
                print(output)
            elif isinstance(updev_dict[updev_key][0], str):
                for data in updev_dict[updev_key]:
                    output = output + data
                    print(output)
            elif isinstance(updev_dict[updev_key][0], dict):
                print(output)
                for nested_dict in updev_dict[updev_key]:
                    self.output_crawler(nested_dict, level+1)

    def get_devices_qubes(self):
        self.get_devices()
        devices_info_dict = json.loads(self.devices_info)
        self.output_crawler(devices_info_dict, 0)

    def get_updates_qubes(self):
        self.get_updates()
        self.parse_updates_info(self.updates_info)
        self.output_crawler(self.updates_info_dict, 0)

    def clean_cache(self):
        pass

    def help(self):
        pass


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
