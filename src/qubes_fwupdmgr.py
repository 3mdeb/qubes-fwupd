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

FWUPD_QUBES_DIR = "/usr/share/qubes-fwupd"
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
FWUPD_DOM0_METADATA_JCAT = os.path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz.jcat"
)
FWUPD_USBVM_LOG = os.path.join(FWUPD_DOM0_DIR, "usbvm-devices.log")
FWUPD_USBVM_VALIDATE = "/usr/share/qubes-fwupd/fwupd_usbvm_validate.py"
FWUPD_USBVM_DIR = "/home/user/.cache/fwupd"
FWUPD_USBVM_UPDATES_DIR = os.path.join(FWUPD_USBVM_DIR, "updates")
FWUPD_USBVM_METADATA_DIR = os.path.join(FWUPD_USBVM_DIR, "metadata")
FWUPD_USBVM_METADATA_SIGNATURE = os.path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_USBVM_METADATA_FILE = os.path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz"
)
FWUPD_USBVM_METADATA_JCAT = os.path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz.jcat"
)
FWUPD_DOWNLOAD_PREFIX = "https://fwupd.org/downloads/"
FWUPDMGR = "/bin/fwupdmgr"
# version > 1.3.8
FWUPDAGENT_NEW = "/bin/fwupdagent"
# version <= 1.3.8
FWUPDAGENT_OLD = "/usr/libexec/fwupd/fwupdagent"
USBVM_N = "sys-usb"

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
    def _download_metadata(self, whonix=False):
        """Initialize downloading metadata files.

        Keywords arguments:
        whonix -- Flag enforces downloading the metadata updates via Tor
        """
        cmd_metadata = [
            FWUPD_DOM0_UPDATE,
            "--metadata"
        ]
        if whonix:
            cmd_metadata.append("--whonix")
        p = subprocess.Popen(cmd_metadata)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Metadata update failed")
        if not os.path.exists(FWUPD_DOM0_METADATA_FILE):
            raise Exception("Metadata signature does not exist")

    def _validate_usbvm_dirs(self):
        """Validates if sys-ubs updates and metadata directories exist."""
        cmd_validate_dirs = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s dirs"' %
            FWUPD_USBVM_VALIDATE
        ]
        p = subprocess.Popen(cmd_validate_dirs)
        p.wait()
        if p.returncode != 0:
            raise Exception("Validation of usbvm directories failed.")

    def _validate_usbvm_archive(self, arch_name, sha):
        """Validates checksum and gpg signature of the archive file."""
        arch_path = os.path.join(FWUPD_USBVM_UPDATES_DIR, arch_name)
        arch_validate = "%s updates %s %s" % (
            FWUPD_USBVM_VALIDATE,
            arch_path,
            sha
        )
        cmd_validate_arch = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s"' %
            arch_validate
        ]
        p = subprocess.Popen(cmd_validate_arch)
        p.wait()
        if p.returncode != 0:
            raise Exception("Validation of the archive file failed.")

    def _copy_usbvm_metadata(self):
        """Copies metadata files to usbvm."""
        cat_file = "cat > %s" % FWUPD_USBVM_METADATA_FILE
        cmd_copy_file = 'cat %s | qvm-run --nogui --pass-io %s "%s"' % (
            FWUPD_DOM0_METADATA_FILE,
            USBVM_N,
            cat_file
        )
        cat_sig = "cat > %s" % FWUPD_USBVM_METADATA_SIGNATURE
        cmd_copy_sig = 'cat %s | qvm-run --nogui --pass-io %s "%s"' % (
            FWUPD_DOM0_METADATA_SIGNATURE,
            USBVM_N,
            cat_sig
        )
        cat_jcat = "cat > %s" % FWUPD_USBVM_METADATA_JCAT
        cmd_copy_jcat = 'cat %s | qvm-run --nogui --pass-io %s "%s"' % (
            FWUPD_DOM0_METADATA_JCAT,
            USBVM_N,
            cat_jcat
        )
        p = subprocess.Popen(cmd_copy_file, shell=True)
        p.wait()
        if p.returncode != 0:
            raise Exception("Copying metadata file failed.")
        p = subprocess.Popen(cmd_copy_sig, shell=True)
        p.wait()
        if p.returncode != 0:
            raise Exception("Copying metadata signature failed.")
        p = subprocess.Popen(cmd_copy_jcat, shell=True)
        p.wait()
        if p.returncode != 0:
            raise Exception("Copying metadata jcat failed.")

    def _validate_usbvm_metadata(self):
        """Checks GPG signature of metadata files in usbvm."""
        cmd_validate_metadata = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s metadata"' %
            FWUPD_USBVM_VALIDATE
        ]
        p = subprocess.Popen(cmd_validate_metadata)
        p.wait()
        if p.returncode != 0:
            raise Exception("Metadata validation failed")

    def _refresh_usbvm_metadata(self):
        """Refreshes metadata in usbvm."""
        cmd_refresh_metadata = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s refresh %s %s lvfs"' %
            (
                FWUPDMGR,
                FWUPD_USBVM_METADATA_FILE,
                FWUPD_USBVM_METADATA_JCAT,
            )
        ]
        p = subprocess.Popen(cmd_refresh_metadata)
        p.wait()
        if p.returncode != 0:
            raise Exception("Metadata refresh in usbvm failed")

    def _copy_firmware_updates(self, arch_name):
        """Copies updates files to usbvm.

        Keywords arguments:
        arch_name - name of the archive file
        """
        arch_path = os.path.join(FWUPD_DOM0_UPDATES_DIR, arch_name)
        output_path = os.path.join(FWUPD_USBVM_UPDATES_DIR, arch_name)
        cat_file = "cat > %s" % output_path
        cmd_copy_file = 'cat %s | qvm-run --nogui --pass-io %s "%s"' % (
            arch_path,
            USBVM_N,
            cat_file
        )
        p = subprocess.Popen(cmd_copy_file, shell=True)
        p.wait()
        if p.returncode != 0:
            raise Exception("Copying metadata file failed.")

    def _install_usbvm_firmware_update(self, arch_name):
        """Installs firmware update for specified device in dom0.

        Keywords arguments:
        arch_name - name of the archive file
        """
        arch_path = os.path.join(FWUPD_USBVM_UPDATES_DIR, arch_name)
        CMD_update = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s install %s" /dev/null' % (
                FWUPDMGR,
                arch_path
            )
        ]
        p = subprocess.Popen(CMD_update)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware update failed")

    def _install_usbvm_firmware_downgrade(self, arch_name):
        """Installs firmware downgrades for specified device in dom0.

        Keywords arguments:
        arch_name - name of the archive file
        """
        arch_path = os.path.join(FWUPD_USBVM_UPDATES_DIR, arch_name)
        CMD_downgrade = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s --allow-older install %s"'
            ' /dev/null' % (
                FWUPDMGR,
                arch_path
            )
        ]
        p = subprocess.Popen(CMD_downgrade)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware downgrade failed")

    def _clean_usbvm(self):
        """Cleans usbvm directories."""
        cmd_clean = [
            "qvm-run",
            "--pass-io",
            USBVM_N,
            'script --quiet --return --command "%s clean"' %
            FWUPD_USBVM_VALIDATE
        ]
        p = subprocess.Popen(cmd_clean)
        p.wait()
        if p.returncode != 0:
            raise Exception("Cleaning usbvm directories failed")

    def refresh_metadata(self, usbvm=False, whonix=False):
        """Updates metadata with downloaded files.

        Keyword arguments:
        usbvm -- usbvm support flag
        whonix -- Flag enforces downloading the metadata updates via Tor
        """
        self._download_metadata(whonix=whonix)
        if usbvm:
            self._validate_usbvm_dirs()
            self._copy_usbvm_metadata()
            self._validate_usbvm_metadata()
            self._refresh_usbvm_metadata()
        cmd_refresh = [
            FWUPDMGR,
            "refresh",
            FWUPD_DOM0_METADATA_FILE,
            FWUPD_DOM0_METADATA_JCAT,
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
            self.fwupdagent_dom0,
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
        """Creates dictionary and list with information about updates.

        Keywords argument:
        updates_info - gathered update information
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

    def _download_firmware_updates(self, url, sha, whonix=False):
        """Initializes downloading firmware upadate archive.

        Keywords arguments:
        url -- url path to the firmware upadate archive
        sha -- SHA1 checksum of the firmware update archive
        whonix -- Flag enforces downloading the updates via Tor
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
        if whonix:
            cmd_fwdownload.append("--whonix")
        p = subprocess.Popen(cmd_fwdownload)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware download failed")
        if not os.path.exists(update_path):
            raise Exception("Firmware update files do not exist")

    def _user_input(self, updates_dict, downgrade=False, usbvm=False):
        """UI for update process.

        Keywords arguments:
        updates_dict - list of updates for specified device
        downgrade -- downgrade flag
        """
        decorator = "======================================================"
        if usbvm:
            updates_list = updates_dict["usbvm"] + updates_dict["dom0"]
        else:
            updates_list = updates_dict["dom0"]
        dom0_updates_num = len(updates_dict["dom0"])-1
        if len(updates_list) == 0:
            print("No updates available.")
            return EXIT_CODES["NO_UPDATES"]
        if downgrade:
            print("Available downgrades:")
        else:
            print("Available updates:")
        self._updates_crawler(updates_dict["dom0"])
        if usbvm:
            self._updates_crawler(
                updates_dict["usbvm"],
                usbvm=True,
                prefix=dom0_updates_num+1
            )

        while True:
            try:
                print("If you want to abandon process press 'N'.")
                choice = input("Otherwise choose a device number: ")
                if choice == 'N' or choice == 'n':
                    return EXIT_CODES["NO_UPDATES"]
                device_num = int(choice)-1
                if 0 <= device_num < len(updates_list):
                    if not downgrade:
                        if device_num > dom0_updates_num:
                            return "usbvm", device_num
                        else:
                            return "dom0", device_num-dom0_updates_num
                    break
                else:
                    raise ValueError()
            except ValueError:
                print("Invalid choice.")

        if downgrade:
            while True:
                try:
                    releases = updates_list[device_num]["Releases"]
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
                    choice = input("Otherwise choose downgrade number: ")
                    if choice == 'N' or choice == 'n':
                        return EXIT_CODES["NO_UPDATES"]
                    downgrade_num = int(choice)-1
                    if 0 <= downgrade_num < len(releases):
                        if device_num > dom0_updates_num:
                            return "usbvm", device_num, downgrade_num
                        else:
                            device_abs_num = device_num - dom0_updates_num
                            return "dom0", device_abs_num, downgrade_num
                    else:
                        raise ValueError()
                except ValueError:
                    print("Invalid choice.")

    def _parse_parameters(self, updates_dict, vm_name, choice):
        """Parses device name, url, version and SHA1 checksum of the file list.

        Keywords arguments:
        updates_dict - dictionary of updates for dom0 and usbvm
        vm_name - VM name
        choice -- number of device to be updated
        """
        self.name = updates_dict[vm_name][choice]["Name"]
        self.version = updates_dict[vm_name][choice]["Releases"][0]["Version"]
        for ver_check in updates_dict[vm_name][choice]["Releases"]:
            if l_ver(ver_check["Version"]) >= l_ver(self.version):
                self.version = ver_check["Version"]
                self.url = ver_check["Url"]
                self.sha = ver_check["Checksum"]

    def _install_dom0_firmware_update(self, arch_path):
        """Installs firmware update for specified device in dom0.

        Keywords arguments:
        arch_path - absolute path to firmware update archive
        """
        cmd_install = [
            FWUPDMGR,
            "install",
            arch_path
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
        """Gathers information about devices connected in dom0."""
        cmd_get_dom0_devices = [
            self.fwupdagent_dom0,
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
        """Gathers information about devices connected in usbvm."""
        if os.path.exists(FWUPD_USBVM_LOG):
            os.remove(FWUPD_USBVM_LOG)
        # Different versions of fwupd have different paths of binaries.
        # In the future the paths will be given dynamically.
        usbvm_cmd = '"%s get-devices"' % self.fwupdagent_usbvm
        cmd_get_usbvm_devices = 'qvm-run --nogui --pass-io %s %s > %s' % (
            USBVM_N,
            usbvm_cmd,
            FWUPD_USBVM_LOG
        )
        p = subprocess.Popen(
            cmd_get_usbvm_devices,
            shell=True
        )
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting usbvm devices info failed")
        if not os.path.exists(FWUPD_USBVM_LOG):
            raise Exception("usbvm device info log does not exist")

    def _parse_usbvm_updates(self, usbvm_devices_info):
        """Creates dictionary and list with information about updates.

        Keywords argument:
        usbvm_devices_info - gathered usbvm information
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
                if not self.usbvm_updates_list[-1]["Releases"]:
                    self.usbvm_updates_list.pop()

    def check_fwupd_version(self, usbvm=False):
        """Checks the fwupd client version and sets fwupdagent paths
        dynamicly

        Keyword arguments:
        usbvm -- usbvm support flag
        """
        version_check = 'client version:\t1.3.8'
        version_regex = re.compile(
            r'client version:\t[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,2}$'
        )
        cmd_version = [
            FWUPDMGR,
            "--version"
        ]
        p = subprocess.Popen(
            cmd_version,
            stdout=subprocess.PIPE
        )
        client_version = p.communicate()[0].decode().split("\n")[0]
        assert version_regex.match(client_version), (
            'Version command output has changed!!!'
        )
        if l_ver(version_check) > l_ver(client_version):
            self.fwupdagent_dom0 = FWUPDAGENT_OLD
        else:
            self.fwupdagent_dom0 = FWUPDAGENT_NEW

        if usbvm:
            cmd_version = f'"{FWUPDMGR}" --version'
            cmd_usbvm_version = [
                'qvm-run',
                '--pass-io',
                USBVM_N,
                cmd_version
            ]
            p = subprocess.Popen(
                cmd_usbvm_version,
                stdout=subprocess.PIPE
            )
            client_version = p.communicate()[0].decode().split("\n")[0]
            assert version_regex.match(client_version), (
                'Version command output has changed!!!'
            )
            if l_ver(version_check) > l_ver(client_version):
                self.fwupdagent_usbvm = FWUPDAGENT_OLD
            else:
                self.fwupdagent_usbvm = FWUPDAGENT_NEW

    def update_firmware(self, usbvm=False, whonix=False):
        """Updates firmware of the specified device.

        Keyword arguments:
        usbvm -- usbvm support flag
        whonix -- Flag enforces downloading the metadata updates via Tor
        """
        self._get_dom0_updates()
        self._parse_dom0_updates_info(self.dom0_updates_info)
        if usbvm:
            self._get_usbvm_devices()
            with open(FWUPD_USBVM_LOG) as usbvm_device_info:
                self._parse_usbvm_updates(usbvm_device_info.read())
            update_dict = {
                "usbvm": self.usbvm_updates_list,
                "dom0": self.dom0_updates_list
            }
            ret_input = self._user_input(update_dict, usbvm=True)
        else:
            update_dict = {
                "dom0": self.dom0_updates_list
            }
            ret_input = self._user_input(update_dict)
        if ret_input == EXIT_CODES["NO_UPDATES"]:
            exit(EXIT_CODES["NO_UPDATES"])
        vm_name, choice = ret_input
        self._parse_parameters(update_dict, vm_name, choice)
        self._download_firmware_updates(self.url, self.sha, whonix=whonix)
        arch_name = self.url.replace(FWUPD_DOWNLOAD_PREFIX, "")
        arch_path = os.path.join(FWUPD_DOM0_UPDATES_DIR, arch_name)
        if self.name == "System Firmware":
            path = arch_path.replace(".cab", "")
            self._verify_dmi(path, self.version)
        if vm_name == "dom0":
            self._install_dom0_firmware_update(arch_path)
        if vm_name == "usbvm":
            self._validate_usbvm_dirs()
            self._copy_firmware_updates(arch_name)
            self._install_usbvm_firmware_update(arch_name)

    def _parse_downgrades(self, device_list):
        """Parses information about possible downgrades.

        Keywords argument:
        device_list -- list of connected devices
        """
        downgrades = []
        dom0_devices_info_dict = json.loads(device_list)
        for device in dom0_devices_info_dict["Devices"]:
            if "Releases" in device:
                try:
                    version = device["Version"]
                except KeyError:
                    continue
                downgrades.append(
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
        return downgrades

    def _install_dom0_firmware_downgrade(self, arch_path):
        """Installs firmware downgrade for specified device.

        Keywords arguments:
        arch_path - absolute path to firmware downgrade archive
        """
        cmd_install = [
            FWUPDMGR,
            "--allow-older",
            "install",
            arch_path
        ]
        p = subprocess.Popen(cmd_install)
        p.wait()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware downgrade failed")

    def downgrade_firmware(self, usbvm=False, whonix=False):
        """Downgrades firmware of the specified device.

        Keyword arguments:
        usbvm -- usbvm support flag
        whonix -- Flag enforces downloading the metadata updates via Tor
        """
        self._get_dom0_devices()
        dom0_downgrades = self._parse_downgrades(self.dom0_devices_info)
        if usbvm:
            self._get_usbvm_devices()
            with open(FWUPD_USBVM_LOG) as usbvm_device_info:
                usbvm_downgrades = self._parse_downgrades(
                    usbvm_device_info.read()
                )
            downgrade_dict = {
                "usbvm": usbvm_downgrades,
                "dom0": dom0_downgrades
            }
            ret_input = self._user_input(
                downgrade_dict,
                downgrade=True,
                usbvm=True
            )
        else:
            downgrade_dict = {
                "dom0": dom0_downgrades
            }
            ret_input = self._user_input(downgrade_dict, downgrade=True)
        if ret_input == EXIT_CODES["NO_UPDATES"]:
            exit(EXIT_CODES["NO_UPDATES"])
        vm_name, device_choice, downgrade_choice = ret_input
        releases = downgrade_dict[vm_name][device_choice]["Releases"]
        downgrade_url = releases[downgrade_choice]["Url"]
        downgrade_sha = releases[downgrade_choice]["Checksum"]
        self._download_firmware_updates(
            downgrade_url,
            downgrade_sha,
            whonix=whonix
        )
        arch_name = downgrade_url.replace(FWUPD_DOWNLOAD_PREFIX, "")
        arch_path = os.path.join(FWUPD_DOM0_UPDATES_DIR, arch_name)
        if downgrade_dict[vm_name][device_choice]["Name"] == "System Firmware":
            path = arch_path.replace(".cab", "")
            self._verify_dmi(
                path,
                downgrade_dict[vm_name][device_choice]["Version"],
                downgrade=True
            )
        if vm_name == "dom0":
            self._install_dom0_firmware_downgrade(arch_path)
        if vm_name == "usbvm":
            self._validate_usbvm_dirs()
            self._copy_firmware_updates(arch_name)
            self._validate_usbvm_archive(arch_name, downgrade_sha)
            self._install_usbvm_firmware_downgrade(arch_name)

    def _output_crawler(self, updev_dict, level, help_f=False, dom0=True):
        """Prints device and updates information as a tree.

        Keywords arguments:
        updev_dict -- update/device information dictionary
        level -- level of the tree
        """
        def _tabs(key_word):
            return key_word + '\t'*(4 - int(len(key_word)/8))

        decorator = "==================================="
        print(2*decorator)
        for updev_key in updev_dict:
            style = '\t'*level
            output = style + _tabs(updev_key + ":")
            if len(updev_key) > 12:
                continue
            if updev_key == "Icons":
                continue
            if updev_key == "Releases":
                continue
            if updev_key == "Name":
                print(style + updev_dict["Name"])
                print(2*decorator)
                continue
            if isinstance(updev_dict[updev_key], str):
                print(output + updev_dict[updev_key])
            elif isinstance(updev_dict[updev_key], int):
                print(output + str(updev_dict[updev_key]))
            elif isinstance(updev_dict[updev_key][0], str):
                for i, data in enumerate(updev_dict[updev_key]):
                    if i == 0:
                        print(output + u'\u00B7' + data)
                        continue
                    print(style + _tabs(' ') + u'\u00B7' + data)
            elif isinstance(updev_dict[updev_key][0], dict):
                if level == 0 and help_f is True:
                    print(output)
                else:
                    if level == 0 and dom0 is True:
                        print("Dom0 " + output)
                    elif level == 0 and dom0 is False:
                        print("%s " % USBVM_N + output)

                for nested_dict in updev_dict[updev_key]:
                    self._output_crawler(nested_dict, level+1)

    def _updates_crawler(self, updates_list, usbvm=False, prefix=0):
        """Prints updates information for dom0 and usbvm

        Keywords arguments:
        updates_list -- list of devices updates
        usbvm -- usbvm support flag
        prefix -- device number prefix
        """
        available_updates = False
        decorator = "======================================================"
        print(decorator)
        if usbvm:
            print("%s updates:" % USBVM_N)
        else:
            print("Dom0 updates:")
        print(decorator)
        if len(updates_list) == 0:
            print("No updates available.")
            return EXIT_CODES["NO_UPDATES"]
        else:
            for i, device in enumerate(updates_list):
                if len(device["Releases"]) == 0:
                    continue
                if not available_updates:
                    print("Available updates:")
                    print(decorator)
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                print("%s. Device: %s" % (i+1+prefix, device["Name"]))
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
                    description = description.replace("</p>", "\n\t")
                    description = description.replace("</li>", "\n\t")
                    print("   Description: %s" % description)
                print(decorator)
                available_updates = True
            if not available_updates:
                print("No updates available.")
                return EXIT_CODES["NO_UPDATES"]

    def get_devices_qubes(self, usbvm=False):
        """Gathers and prints devices information.

        Keyword arguments:
        usbvm -- usbvm support flag
        """
        self._get_dom0_devices()
        dom0_devices_info_dict = json.loads(self.dom0_devices_info)
        self._output_crawler(dom0_devices_info_dict, 0)
        if usbvm:
            self._get_usbvm_devices()
            with open(FWUPD_USBVM_LOG) as usbvm_device_info:
                usbvm_device_info_dict = json.loads(usbvm_device_info.read())
            self._output_crawler(usbvm_device_info_dict, 0, dom0=False)

    def get_updates_qubes(self, usbvm=False):
        """Gathers and prints updates information.

        Keyword arguments:
        usbvm -- usbvm support flag
        """
        self._get_dom0_updates()
        self._parse_dom0_updates_info(self.dom0_updates_info)
        self._updates_crawler(self.dom0_updates_list)
        if usbvm:
            self._get_usbvm_devices()
            with open(FWUPD_USBVM_LOG) as usbvm_device_info:
                self._parse_usbvm_updates(usbvm_device_info.read())
            self._updates_crawler(self.usbvm_updates_list, usbvm=True)

    def clean_cache(self, usbvm=False):
        """Removes updates data

        Keyword arguments:
        usbvm -- usbvm support flag
        """
        print("Cleaning dom0 cache directories")
        if os.path.exists(FWUPD_DOM0_METADATA_DIR):
            shutil.rmtree(FWUPD_DOM0_METADATA_DIR)
        if os.path.exists(FWUPD_DOM0_UPDATES_DIR):
            shutil.rmtree(FWUPD_DOM0_UPDATES_DIR)
        if usbvm:
            print("Cleaning usbvm cache directories")
            self._clean_usbvm()

    def help(self):
        """Prints help information"""
        self._output_crawler(HELP, 0, help_f=True)

    def check_usbvm(self):
        """Checks if usbvm is running"""
        cmd_xl_list = [
            "xl",
            "list"
        ]
        p = subprocess.Popen(
                cmd_xl_list,
                stdout=subprocess.PIPE
            )
        self.output = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Firmware downgrade failed")
        return USBVM_N in self.output


def main():
    if os.geteuid() != 0:
        print("You need to have root privileges to run this script.\n")
        exit(EXIT_CODES["ERROR"])
    q = QubesFwupdmgr()
    sys_usb = q.check_usbvm()
    q.check_fwupd_version(usbvm=sys_usb)
    if not os.path.exists(FWUPD_DOM0_DIR):
        q.refresh_metadata(usbvm=sys_usb)
    if len(sys.argv) < 2:
        q.help()
    elif sys.argv[1] == "get-updates":
        q.get_updates_qubes(usbvm=sys_usb)
    elif sys.argv[1] == "get-devices":
        q.get_devices_qubes(usbvm=sys_usb)
    elif sys.argv[1] == "refresh" and "--whonix" in sys.argv:
        q.refresh_metadata(usbvm=sys_usb, whonix=True)
    elif sys.argv[1] == "refresh" and "--whonix" not in sys.argv:
        q.refresh_metadata(usbvm=sys_usb)
    elif sys.argv[1] == "update" and "--whonix" in sys.argv:
        q.update_firmware(usbvm=sys_usb, whonix=True)
    elif sys.argv[1] == "update" and "--whonix" not in sys.argv:
        q.update_firmware(usbvm=sys_usb)
    elif sys.argv[1] == "downgrade" and "--whonix" in sys.argv:
        q.downgrade_firmware(usbvm=sys_usb, whonix=True)
    elif sys.argv[1] == "downgrade" and "--whonix" not in sys.argv:
        q.downgrade_firmware(usbvm=sys_usb)
    elif sys.argv[1] == "clean":
        q.clean_cache(usbvm=sys_usb)
    else:
        q.help()


if __name__ == '__main__':
    main()
