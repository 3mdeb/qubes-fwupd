#!/usr/bin/python3

import grp
import glob
import hashlib
import os
import os.path as path
import re
import shutil
import subprocess
import sys

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

WARNING_COLOR = '\033[93m'


class FwupdUsbvmUpdates:
    def _create_dirs(self, *args):
        """Method creates directories.

        Keyword arguments:
        *args -- paths to be created
        """
        qubes_gid = grp.getgrnam('qubes').gr_gid
        self.old_umask = os.umask(0o002)
        if args is None:
            raise Exception("Creating directories failed, no paths given.")
        for file_path in args:
            if not path.exists(file_path):
                os.mkdir(file_path)
                os.chown(file_path, -1, qubes_gid)
                os.chmod(file_path, 0o0775)
            elif os.stat(file_path) != qubes_gid:
                print(
                    WARNING_COLOR +
                    "Warning: You should move a personal files from %s. "
                    % 'test.py' +
                    "Cleaning cache will cause lose of the personal data!!" +
                    WARNING_COLOR
                )

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

    def validate_dirs(self):
        """Validates and creates directories"""
        if os.path.exists(FWUPD_USBVM_METADATA_DIR):
            shutil.rmtree(FWUPD_USBVM_METADATA_DIR)
            self._create_dirs(FWUPD_USBVM_METADATA_DIR)
        else:
            self._create_dirs(FWUPD_USBVM_METADATA_DIR)
        if not os.path.exists(FWUPD_USBVM_UPDATES_DIR):
            self._create_dirs(FWUPD_USBVM_UPDATES_DIR)
        os.umask(self.old_umask)

    def clean(self):
        """Removes updates data"""
        print("Cleaning cache directories")
        if os.path.exists(FWUPD_USBVM_METADATA_DIR):
            shutil.rmtree(FWUPD_USBVM_METADATA_DIR)
        if os.path.exists(FWUPD_USBVM_UPDATES_DIR):
            shutil.rmtree(FWUPD_USBVM_UPDATES_DIR)

    def validate_metadata(self):
        """Validates received the metadata files."""
        try:
            self._gpg_verification(FWUPD_USBVM_METADATA_FILE)
        except Exception:
            self.clean()

    def validate_updates(self, archive_path, sha):
        """Validates recived an update file.

        Keyword arguments:
        archive_path - path to the firmware update archive
        sha -- SHA1 checksum of the firmware update archive
        """
        self._check_shasum(archive_path, sha)
        output_path = archive_path.replace(".cab", "")
        self._extract_archive(archive_path, output_path)
        signature_name = path.join(output_path, "firmware*.asc")
        file_path = glob.glob(signature_name)
        try:
            self._gpg_verification(file_path[0].replace(".asc", ""))
        except Exception:
            self.clean()


def main():
    f = FwupdUsbvmUpdates()
    if len(sys.argv) < 2:
        raise Exception("Invalid number of arguments.")
    if sys.argv[1] == "metadata":
        f.validate_metadata()
    if sys.argv[1] == "dirs":
        f.validate_dirs()
    if sys.argv[1] == "clean":
        f.clean()
    if sys.argv[1] == "updates":
        if len(sys.argv) < 4:
            raise Exception(
                "Invalid number of arguments.\n"
                "Expected archive path and checksum."
            )
        f.validate_updates(sys.argv[3], sys.argv[4])
