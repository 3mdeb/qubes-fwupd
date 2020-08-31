#!/usr/bin/python3
import src.qubes_fwupdmgr as qfwupd
import subprocess
import os
import shutil
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
                if line.startswith("BiosVersion: CBET"):
                    self.heads_version = line.replace("BiosVersion: CBET", "")
        else:
            print("Device is not running under the heads firmware!!")
            print("Exiting...")
            return qfwupd.EXIT_CODES["NO_UPDATES"]

    def _check_heads_updates(self):
        """
        Checks if updates exist and informs user about the result.
        """
        self.heads_update_url = None
        self.heads_update_sha = None
        self.heads_update_version = None
        return qfwupd.EXIT_CODES["SUCCESS"]

    def _copy_heads_firmware(self):
        """
        """
        heads_boot_path = os.path.join(
            HEADS_UPDATES_DIR,
            self.heads_update_version
        )
        update_path = self.arch_path.replace(".cab", "/coreboot.rom")
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

    def heads_update(self, whonix=False):
        """
        Updates heads system firmware
        """
        self._get_hwids()
        if self._gather_firmware_version() == qfwupd.EXIT_CODES["NO_UPDATES"]:
            return qfwupd.EXIT_CODES["NO_UPDATES"]
        self._check_heads_updates()
        self._download_firmware_updates(
            self.heads_update_url,
            self.heads_update_sha
        )
        if self._copy_heads_firmware() == qfwupd.EXIT_CODES["NO_UPDATES"]:
            exit(qfwupd.EXIT_CODES["NO_UPDATES"])
        elif self._copy_heads_firmware() == qfwupd.EXIT_CODES["SUCCESS"]:
            exit(qfwupd.EXIT_CODES["SUCCESS"])
        else:
            raise Exception("Copying heads update failed!!")
