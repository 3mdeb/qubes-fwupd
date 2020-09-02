#!/usr/bin/python3
import src.qubes_fwupdmgr as qfwupd
import subprocess
import os
import shutil
import xml.etree.ElementTree as ET
from distutils.version import LooseVersion as l_ver

BOOT = "/boot"
HEADS_UPDATES_DIR = os.path.join(BOOT, "update")
HEADS_COREBOOT = os.path.join(HEADS_UPDATES_DIR, "coreboot.rom")


class FwupdHeads(qfwupd.QubesFwupdmgr):
    def _get_hwids(self):
        cmd_hwids = [qfwupd.FWUPDMGR, "hwids"]
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
                    )
        else:
            print("Device is not running under the heads firmware!!")
            print("Exiting...")
            return qfwupd.EXIT_CODES["NO_UPDATES"]

    def _parse_metadata(self):
        """
        Parse metadata info.
        """
        cmd_metadata = ["zcat", self.metadata_file]
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
            return qfwupd.EXIT_CODES["NO_UPDATES"]
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
            return qfwupd.EXIT_CODES["SUCCESS"]
        else:
            return qfwupd.EXIT_CODES["NO_UPDATES"]

    def _copy_heads_firmware(self):
        """
        Copies heads update to the boot path
        """
        heads_boot_path = os.path.join(
            HEADS_UPDATES_DIR,
            self.heads_update_version
        )
        update_path = self.arch_path.replace(".cab", "/firmware.rom")
        if not os.path.exists(HEADS_UPDATES_DIR):
            os.mkdir(HEADS_UPDATES_DIR)
        if os.path.exists(heads_boot_path):
            print(
                f"Heads Update == {self.heads_update_version} "
                "already exists"
            )
            return qfwupd.EXIT_CODES["NO_UPDATES"]
        else:
            shutil.copyfile(update_path, heads_boot_path)
            print(
                f"Heads Update == {self.heads_update_version} "
                f"available at {heads_boot_path}"
            )
            return qfwupd.EXIT_CODES["SUCCESS"]

    def heads_update(self, device="x230", whonix=False, metadata_url=None):
        """
        Updates heads firmware

        Keyword arguments:
        device -- Model of the updated device
        whonix -- Flag enforces downloading the metadata updates via Tor
        metadata_url -- Use custom metadata from the url
        """
        if metadata_url:
            custom_metadata_name = metadata_url.replace(
                qfwupd.FWUPD_DOWNLOAD_PREFIX,
                ""
            )
            self.metadata_file = os.path.join(
                qfwupd.FWUPD_DOM0_METADATA_DIR,
                custom_metadata_name
            )
        else:
            self.metadata_file = qfwupd.FWUPD_DOM0_METADATA_FILE
        self._get_hwids()
        if not os.path.isfile(self.metadata_file):
            self._download_metadata(whonix=whonix, metadata_url=metadata_url)
        self._parse_metadata()
        if self._gather_firmware_version() == qfwupd.EXIT_CODES["NO_UPDATES"]:
            return qfwupd.EXIT_CODES["NO_UPDATES"]
        self._parse_heads_updates(device)
        self._download_firmware_updates(
            self.heads_update_url,
            self.heads_update_sha
        )
        return_code = self._copy_heads_firmware()
        if return_code == qfwupd.EXIT_CODES["NO_UPDATES"]:
            exit(qfwupd.EXIT_CODES["NO_UPDATES"])
        elif return_code == qfwupd.EXIT_CODES["SUCCESS"]:
            print()
            while True:
                try:
                    print("An update requires a reboot to complete.")
                    choice = input("Do you want to restart now? (Y|N)")
                    if choice == 'N' or choice == 'n':
                        return qfwupd.EXIT_CODES["SUCCESS"]
                    elif choice == 'Y' or choice == 'y':
                        print("Rebooting...")
                        os.system("reboot")
                    else:
                        raise ValueError()
                except ValueError:
                    print("Invalid choice.")

        else:
            raise Exception("Copying heads update failed!!")
