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
        updates_info_dict = json.loads(updates_info)
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
            ] for device in updates_info_dict["Devices"]
        ]

    def download_firmware_updates(self, url, sha):
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

#    def user_input(self,)
#       self.get_updates()
#       if
#       self.parse_updates_info(self.updates_info)
#       self.user_choice
