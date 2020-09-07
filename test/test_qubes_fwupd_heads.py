#!/usr/bin/python3
import io
import os
import platform
import shutil
import src.qubes_fwupd_heads as qf_heads
import src.qubes_fwupdmgr as qfwupd
import sys
import unittest

from test.fwupd_logs import HEADS_XML

CUSTOM_METADATA = "https://fwupd.org/downloads/firmware-3c81bfdc9db5c8a42c09d38091944bc1a05b27b0.xml.gz"


class TestQubesFwupdHeads(unittest.TestCase):
    def setUp(self):
        self.q = qf_heads.FwupdHeads()
        self.maxDiff = 2000
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_get_hwids(self):
        self.q._check_fwupdtool_version()
        self.q._get_hwids()
        self.assertNotEqual(self.q.dom0_hwids_info, "")

    def test_gather_firmware_version_empty(self):
        self.q.dom0_hwids_info = ""
        return_code = self.q._gather_firmware_version()
        self.assertEqual(return_code, 99)

    def test_gather_firmware_version(self):
        self.q.dom0_hwids_info = "BiosVersion: CBET4000 4.13 heads"
        self.q._gather_firmware_version()
        self.assertEqual(self.q.heads_version, "4.13 heads")

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_parse_metadata(self):
        qmgr = qfwupd.QubesFwupdmgr()
        qmgr.metadata_file = CUSTOM_METADATA.replace(
            "https://fwupd.org/downloads",
            qfwupd.FWUPD_DOM0_METADATA_DIR
        )
        qmgr._download_metadata(metadata_url=CUSTOM_METADATA)
        self.q._parse_metadata(qmgr.metadata_file)
        self.assertTrue(self.q.metadata_info)

    def test_check_heads_updates_default_heads(self):
        self.q.metadata_info = HEADS_XML
        self.q.heads_version = "heads"
        return_code = self.q._parse_heads_updates("x230")
        self.assertEqual(return_code, 0)
        self.assertEqual(
            self.q.heads_update_url,
            "https://fwupd.org/downloads/10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab"
        )
        self.assertEqual(
            self.q.heads_update_sha,
            "cf3af2382cbd3c438281d33daef63b69af7854cd"
        )
        self.assertEqual(
            self.q.heads_update_version,
            "4.19.0"
        )

    def test_check_heads_updates_no_updates(self):
        self.q.metadata_info = HEADS_XML
        self.q.heads_version = "4.19.0 heads"
        return_code = self.q._parse_heads_updates("x230")
        self.assertEqual(return_code, 99)

    def test_check_heads_updates_lower_version(self):
        self.q.metadata_info = HEADS_XML
        self.q.heads_version = "4.17.0 heads"
        return_code = self.q._parse_heads_updates("x230")
        self.assertEqual(return_code, 0)
        self.assertEqual(
            self.q.heads_update_url,
            "https://fwupd.org/downloads/10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab"
        )
        self.assertEqual(
            self.q.heads_update_sha,
            "cf3af2382cbd3c438281d33daef63b69af7854cd"
        )
        self.assertEqual(
            self.q.heads_update_version,
            "4.19.0"
        )

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_copy_heads_firmware(self):
        qmgr = qfwupd.QubesFwupdmgr()
        self.q.heads_update_url = "https://fwupd.org/downloads/10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab"
        self.q.heads_update_sha = "cf3af2382cbd3c438281d33daef63b69af7854cd"
        self.q.heads_update_version = "4.19.0"
        qmgr._download_firmware_updates(
            self.q.heads_update_url,
            self.q.heads_update_sha
        )
        heads_boot_path = os.path.join(
            qf_heads.HEADS_UPDATES_DIR,
            self.q.heads_update_version
        )
        if os.path.exists(heads_boot_path):
            shutil.rmtree(heads_boot_path)
        ret_code = self.q._copy_heads_firmware(qmgr.arch_path)
        self.assertNotEqual(ret_code, qfwupd.EXIT_CODES["NO_UPDATES"])
        firmware_path = os.path.join(heads_boot_path, "firmware.rom")
        self.assertTrue(os.path.exists(firmware_path))


if __name__ == '__main__':
    unittest.main()
