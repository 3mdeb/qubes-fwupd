import src.qubes_fwupdmgr as qfwupd
import subprocess

from distutils.version import LooseVersion as l_ver


# May differ in older versions of the fwupd
FWUPDTOOL = "fwupdtool"


class fwupd_heads(qfwupd.QubesFwupdmgr):
    def _get_hwids(self):
        cmd_hwids = [FWUPDTOOL, "hwids"]
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
            print("Device do not run under the heads firmware system!!!")
            print("Exiting...")
            exit(1)

    def _check_heads_updates(self):
        """
        Checks if updates exist and informs user about the result.
        """
        self.heads_update_url = None
        self.heads_update_sha = None
        return qfwupd.EXIT_CODES["SUCCESS"]

    def heads_update(self, whonix=False):
        """
        Updates heads system firmware
        """
        self._get_hwids()
        self._gather_firmware_version()
        if self.heads_version is None:
            raise Exception("Getting heads version failed")
        self._check_heads_updates()
        self._download_firmware_updates(
            self.heads_update_url,
            self.heads_update_sha
        )
