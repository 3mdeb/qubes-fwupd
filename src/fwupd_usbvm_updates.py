#!/usr/bin/python3

import hashlib
import os
import os.path as path
import re
import shutil
import subprocess

FWUPD_USBVM_DIR = "/home/user/.cache/fwupd"
FWUPD_USBVM_UPDATES_DIR = path.join(FWUPD_USBVM_DIR, "updates")
FWUPD_USBVM_METADATA_DIR = os.path.join(FWUPD_USBVM_DIR, "metadata")
FWUPD_USBVM_METADATA_SIGNATURE = os.path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_USBVM_METADATA_FILE = os.path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz"
)
FWUPDMGR = "/bin/fwupdmgr"

GPG_LVFS_REGEX = re.compile(
    r"gpg: Good signature from [a-z0-9\[\]\@\<\>\.\"\"]{1,128}"
)


class FwupdUsbvmUpdates:
    def _check_shasum(self, file_path, sha):
        """Compares computed SHA1 checksum with `sha` parameter.

        Keyword arguments:
        file_path -- absolute path to the file
        sha -- SHA1 checksum of the file
        """
        with open(file_path, 'rb') as f:
            c_sha = hashlib.sha1(f.read()).hexdigest()
        if c_sha != sha:
            raise ValueError(
                "Computed checksum %s did NOT match %s. " %
                (c_sha, sha)
            )

    def _verify_received(self, files_path, regex_pattern):
        """Checks if sent files match  regex filename pattern.

        Keyword arguments:

        files_path -- absolute path to inspected directory
        regex_pattern -- pattern of the expected files
        """
        for untrusted_f in os.listdir(files_path):
            if not regex_pattern.match(untrusted_f):
                raise Exception(
                    'Dom0 sent unexpected file'
                )
            f = untrusted_f
            assert '/' not in f
            assert '\0' not in f
            assert '\x1b' not in f
            path_f = path.join(files_path, f)
            if os.path.islink(path_f) or not os.path.isfile(path_f):
                raise Exception(
                    'Dom0 sent not regular file'
                )

    def _extract_archive(self, archive_path, output_path):
        """Extracts archive file to the specified directory.

        Keyword arguments:
        archive_path -- absolute path to archive file
        output_path -- absolute path to the output directory
        """
        cmd_extract = [
            "cabextract",
            "-d",
            "%s" % output_path,
            "%s" % archive_path
        ]
        shutil.copy(archive_path, FWUPD_USBVM_UPDATES_DIR)
        p = subprocess.Popen(cmd_extract, stdout=subprocess.PIPE)
        p.communicate()[0].decode('ascii')
        if p.returncode != 0:
            raise Exception(
                'cabextract: Error while extracting %s.' %
                archive_path
            )

    def _gpg_verification(self, file_path):
        """Verifies GPG signature.

        Keyword argument:
        file_path -- absolute path to inspected file
        """
        cmd_gpg = [
            "gpg",
            "--verify",
            "%s.asc" % file_path,
            "%s" % file_path,
        ]
        p = subprocess.Popen(
            cmd_gpg,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        __, stderr = p.communicate()
        verification = stderr.decode('ascii')
        print(verification)
        if p.returncode != 0:
            raise Exception('gpg: Verification failed')
        if not GPG_LVFS_REGEX.search(verification.strip()):
            raise Exception(
                'Domain updateVM sent not signed firmware: ' + file_path
            )

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

    def refresh_metadata(self):
        """Updates metadata with downloaded files."""
        cmd_refresh = [
            FWUPDMGR,
            "refresh",
            FWUPD_USBVM_METADATA_FILE,
            FWUPD_USBVM_METADATA_SIGNATURE,
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
