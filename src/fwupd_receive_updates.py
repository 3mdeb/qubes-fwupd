#!/usr/bin/python3
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2010  Rafal Wojtczuk  <rafal@invisiblethingslab.com>
#               2020  Norbert Kamiński  <norbert.kaminski@3mdeb.com>
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
import glob
import grp
import hashlib
import os
import os.path as path
import re
import shutil
import sys
import subprocess

FWUPD_DOM0_DIR = "/root/.cache/fwupd"
FWUPD_DOM0_UPDATES_DIR = path.join(FWUPD_DOM0_DIR, "updates")
FWUPD_DOM0_UNTRUSTED_DIR = path.join(FWUPD_DOM0_UPDATES_DIR, "untrusted")
FWUPD_DOM0_METADATA_DIR = path.join(FWUPD_DOM0_DIR, "metadata")
FWUPD_DOM0_METADATA_SIGNATURE = path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_DOM0_METADATA_FILE = path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz"
)

FWUPD_UPDATEVM_DIR = "/home/user/.cache/fwupd"
FWUPD_UPDATEVM_UPDATES_DIR = path.join(FWUPD_UPDATEVM_DIR, "updates")
FWUPD_UPDATEVM_METADATA_DIR = path.join(FWUPD_UPDATEVM_DIR, "metadata")
FWUPD_UPDATEVM_METADATA_SIGNATURE = path.join(
    FWUPD_UPDATEVM_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_UPDATEVM_METADATA_FILE = path.join(
    FWUPD_UPDATEVM_METADATA_DIR,
    "firmware.xml.gz"
)

FWUPD_METADATA_FILES_REGEX = re.compile(r"^firmware.xml.gz.?a?s?c?$")
FWUPD_FIRMWARE_FLAG_REGEX = re.compile(r"^updateflag-[A-Za-z0-9]{1,128}\.cab")
FWUPD_METADATA_FLAG_REGEX = re.compile(r"^metaflag")
GPG_LVFS_REGEX = re.compile(
    r"gpg: Good signature from [a-z0-9\[\]\@\<\>\.\"\"]{1,128}"
)
WARNING_COLOR = '\033[93m'


class FwupdReceiveUpdates:
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

    def _check_domain(self, updatevm):
        """Checks if domain given as `updatevm` is allowed to send update
        files.

        Keyword argument:
        updatevm - domain to be checked
        """
        cmd = ['qubes-prefs', '--force-root', 'updatevm']
        p = subprocess.check_output(cmd)
        self.source = p.decode('ascii').rstrip()
        if self.source != updatevm:
            print(
                'Domain ' + str(self.source) +
                'not allowed to send dom0 updates',
                file=sys.stderr
            )
            exit(1)

    def _verify_received(self, files_path, regex_pattern):
        """Checks if sent files match  regex filename pattern.

        Keyword arguments:

        files_path -- absolute path to inspected directory
        regex_pattern -- pattern of the expected files
        """
        for untrusted_f in os.listdir(files_path):
            if not regex_pattern.match(untrusted_f):
                raise Exception(
                    'Domain ' + self.source + ' sent unexpected file'
                )
            f = untrusted_f
            assert '/' not in f
            assert '\0' not in f
            assert '\x1b' not in f
            path_f = path.join(files_path, f)
            if os.path.islink(path_f) or not os.path.isfile(path_f):
                raise Exception(
                    'Domain ' + self.source + ' sent not regular file'
                )

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
        shutil.copy(archive_path, FWUPD_DOM0_UPDATES_DIR)
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

    def handle_fw_update(self, updatevm, sha, filename):
        """Copies firmware update archives from the updateVM.

        Keyword arguments:
        updatevm -- update VM name
        sha -- SHA1 checksum of the firmware update archive
        filename -- name of the firmware update archive
        """
        fwupd_firmware_file_regex = re.compile(filename)
        dom0_firmware_untrusted_path = os.path.join(
            FWUPD_DOM0_UNTRUSTED_DIR,
            filename
        )
        updatevm_firmware_file_path = os.path.join(
            FWUPD_UPDATEVM_UPDATES_DIR,
            filename
        )

        self._check_domain(updatevm)
        self._create_dirs(FWUPD_DOM0_UPDATES_DIR, FWUPD_DOM0_UNTRUSTED_DIR)

        cmd = "/usr/bin/qvm-run --pass-io "
        cmd.join(self.source)
        cmd.join(" 'cat %s' > " % updatevm_firmware_file_path)
        cmd.join(dom0_firmware_untrusted_path)
        if os.system(cmd):
            raise Exception('qvm-run: Copying firmware file failed!!')

        self._verify_received(
            FWUPD_DOM0_UNTRUSTED_DIR,
            fwupd_firmware_file_regex
        )
        self._check_shasum(dom0_firmware_untrusted_path, sha)
        untrusted_dir_name = filename.replace(".cab", "")
        output_path = path.join(FWUPD_DOM0_UNTRUSTED_DIR, untrusted_dir_name)
        self._extract_archive(dom0_firmware_untrusted_path, output_path)
        signature_name = path.join(output_path, "firmware*.asc")
        file_path = glob.glob(signature_name)
        self._gpg_verification(file_path[0].replace(".asc", ""))
        os.umask(self.old_umask)
        dir_name = path.join(FWUPD_DOM0_UPDATES_DIR, untrusted_dir_name)
        shutil.move(output_path, dir_name)
        shutil.rmtree(FWUPD_DOM0_UNTRUSTED_DIR)
        exit(0)

    def handle_metadata_update(self, updatevm):
        """Copies metadata files from the updateVM.

        Keyword argument:
        updatevm -- update VM name
        """
        self._check_domain(updatevm)
        self._create_dirs(FWUPD_DOM0_METADATA_DIR)

        cmd = "/usr/bin/qvm-run --pass-io "
        cmd.join(self.source)
        cmd_signature = cmd.join(
            " 'cat %s' > " % FWUPD_UPDATEVM_METADATA_SIGNATURE
        )
        cmd_signature.join(FWUPD_DOM0_METADATA_SIGNATURE)
        cmd.join(" 'cat %s' > " % FWUPD_UPDATEVM_METADATA_FILE)
        cmd.join(FWUPD_DOM0_METADATA_FILE)
        if os.system(cmd):
            raise Exception('qvm-run: Copying metadata file failed!!')
        if os.system(cmd_signature):
            raise Exception('qvm-run": Copying metadata signature failed!!')

        self._verify_received(
            FWUPD_DOM0_METADATA_DIR,
            FWUPD_METADATA_FILES_REGEX
        )
        self._gpg_verification(FWUPD_DOM0_METADATA_FILE)
        os.umask(self.old_umask)
        exit(0)


def main():
    updatevm = sys.argv[1]
    fwupd = FwupdReceiveUpdates()
    if updatevm is None:
        exit(1)
    if sys.argv[2] is None:
        raise Exception("No flag mode has been set!!!")
    elif sys.argv[2] == "metadata":
        fwupd.handle_metadata_update(updatevm)
    elif sys.argv[2] == "update":
        fwupd.handle_fw_update(updatevm, sys.argv[3], sys.argv[4])


if __name__ == '__main__':
    main()
