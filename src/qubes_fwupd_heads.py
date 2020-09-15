#!/usr/bin/python3
import subprocess
import os
import re
import shutil
import xml.etree.ElementTree as ET
from distutils.version import LooseVersion as l_ver

FWUPDMGR = "/bin/fwupdmgr"
FWUPDTOOL = "/bin/fwupdtool"
FWUPDTOOL_OLD = "/usr/libexec/fwupd/fwupdtool"
FWUPDNEWS = "/usr/share/doc/fwupd/NEWS"

USBVM_N = "sys-usb"

BOOT = "/boot"
HEADS_UPDATES_DIR = os.path.join(BOOT, "updates")
HEADS_COREBOOT = os.path.join(HEADS_UPDATES_DIR, "coreboot.rom")
FWUPD_DOM0_UPDATES_DIR = "/root/.cache/fwupd/updates"

EXIT_CODES = {
    "ERROR": 1,
    "SUCCESS": 0,
    "NO_UPDATES": 99,
}


class FwupdHeads:
    def _get_hwids(self):
        cmd_hwids = [self.fwupd_hwids, "hwids"]
        p = subprocess.Popen(
            cmd_hwids,
            stdout=subprocess.PIPE
        )
        self.dom0_hwids_info = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Getting hwids info failed")

    def _gather_firmware_version(self):
        """
        Checks if Qubes works under heads
        """
        if "heads" in self.dom0_hwids_info:
            self.heads_version = None
            hwids = self.dom0_hwids_info.split("\n")
            for line in hwids:
                if line.startswith("BiosVersion: CBET4000 "):
                    self.heads_version = line.replace(
                        "BiosVersion: CBET4000 ",
                        ""
                    ).replace(
                        " heads",
                        ""
                    )
        else:
            print("Device is not running under the heads firmware!!")
            print("Exiting...")
            return EXIT_CODES["NO_UPDATES"]

    def _parse_metadata(self, metadata_file):
        """
        Parse metadata info.
        """
        cmd_metadata = ["zcat", metadata_file]
        p = subprocess.Popen(
            cmd_metadata,
            stdout=subprocess.PIPE
        )
        self.metadata_info = p.communicate()[0].decode()
        if p.returncode != 0:
            raise Exception("fwudp-qubes: Parsing metadata failed")

    def _parse_heads_updates(self, device):
        """
        Parses heads updates info.

        Keyword arguments:
        device -- Model of the updated device
        """
        self.heads_update_url = None
        self.heads_update_sha = None
        self.heads_update_version = None
        heads_metadata_info = None
        root = ET.fromstring(self.metadata_info)
        for component in root.findall("component"):
            if f"heads.{device}" in component.find("id").text:
                heads_metadata_info = component
        if not heads_metadata_info:
            print("No metadata info for chosen board")
            return EXIT_CODES["NO_UPDATES"]
        for release in heads_metadata_info.find("releases").findall("release"):
            release_ver = release.get("version")
            if (self.heads_version == "heads" or
                    l_ver(release_ver) > l_ver(self.heads_version)):
                if (not self.heads_update_version or
                        l_ver(release_ver) > l_ver(self.heads_update_version)):
                    self.heads_update_url = release.find("location").text
                    for sha in release.findall("checksum"):
                        if (".cab" in sha.attrib["filename"]
                                and sha.attrib["type"] == "sha1"):
                            self.heads_update_sha = sha.text
                    self.heads_update_version = release_ver
        if self.heads_update_url:
            return EXIT_CODES["SUCCESS"]
        else:
            print("Heads firmware is up to date.")
            return EXIT_CODES["NO_UPDATES"]

    def _copy_heads_firmware(self, arch_path):
        """
        Copies heads update to the boot path
        """
        heads_boot_path = os.path.join(
            HEADS_UPDATES_DIR,
            self.heads_update_version
        )
        update_path = arch_path.replace(".cab", "/firmware.rom")

        heads_update_path = os.path.join(
            heads_boot_path,
            "firmware.rom"
        )
        if not os.path.exists(HEADS_UPDATES_DIR):
            os.mkdir(HEADS_UPDATES_DIR)
        if os.path.exists(heads_update_path):
            print(
                f"Heads Update == {self.heads_update_version} "
                "already downloaded."
            )
            return EXIT_CODES["NO_UPDATES"]
        else:
            os.mkdir(heads_boot_path)
            shutil.copyfile(update_path, heads_update_path)
            print(
                f"Heads Update == {self.heads_update_version} "
                f"available at {heads_boot_path}"
            )
            return EXIT_CODES["SUCCESS"]

    def _check_fwupdtool_version(self):
        """Checks the fwupd client version and sets fwupdtool path dynamically
        """
        version_check = 'client version:\t1.3.6'
        version_check_old = 'client version:\t1.1.2'
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
        self.client_version = p.communicate()[0].decode().split("\n")[0]
        if p.returncode != 0 and not os.path.exists(FWUPDNEWS):
            raise Exception("Checking version failed")
        elif p.returncode != 0 and os.path.exists(FWUPDNEWS):
            with open(FWUPDNEWS, "r") as news:
                self.client_version = news.readline().replace(
                    "Version ",
                    "client version:\t"
                )
                self.client_version = self.client_version.replace("\n", "")
        assert version_regex.match(self.client_version), (
            'Version command output has changed!!!'
        )
        if l_ver(version_check_old) > l_ver(self.client_version):
            self.fwupd_hwids = FWUPDMGR
        elif l_ver(version_check) > l_ver(self.client_version):
            self.fwupd_hwids = FWUPDTOOL_OLD
        else:
            self.fwupd_hwids = FWUPDTOOL
