#!/usr/bin/python3

import grp
import hashlib
import os
import shutil

FWUPD_VM_DIR = "/home/user/.cache/fwupd"
FWUPD_VM_UPDATES_DIR = os.path.join(FWUPD_VM_DIR, "updates")
FWUPD_VM_METADATA_DIR = os.path.join(FWUPD_VM_DIR, "metadata")
WARNING_COLOR = '\033[93m'


class FwupdVmCommon:
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
            if not os.path.exists(file_path):
                os.mkdir(file_path)
                os.chown(file_path, -1, qubes_gid)
            elif os.stat(file_path).st_gid != qubes_gid:
                print(
                    f"{WARNING_COLOR}Warning: You should move a personal files"
                    f" from {file_path}. Cleaning cache will cause lose of "
                    f"the personal data!!{WARNING_COLOR}"
                )

    def check_shasum(self, file_path, sha):
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

    def validate_dirs(self):
        """Validates and creates directories"""
        print("Validating directories")
        if not os.path.exists(FWUPD_VM_DIR):
            self._create_dirs(FWUPD_VM_DIR)
        if os.path.exists(FWUPD_VM_METADATA_DIR):
            shutil.rmtree(FWUPD_VM_METADATA_DIR)
            self._create_dirs(FWUPD_VM_METADATA_DIR)
        else:
            self._create_dirs(FWUPD_VM_METADATA_DIR)
        if not os.path.exists(FWUPD_VM_UPDATES_DIR):
            self._create_dirs(FWUPD_VM_UPDATES_DIR)
        os.umask(self.old_umask)
