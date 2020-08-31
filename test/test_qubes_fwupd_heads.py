#!/usr/bin/python3
import io
import platform
import sys
import unittest
import src.qubes_fwupd_heads as qf_heads


class TestQubesFwupdHeads(unittest.TestCase):
    def setUp(self):
        self.q = qf_heads.FwupdHeads()
        self.maxDiff = 2000
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_get_hwids(self):
        self.q._get_hwids()
        self.assertNotEqual(self.q.dom0_hwids_info, "")

    def test_gather_firmware_version_empty(self):
        self.q.dom0_hwids_info = ""
        return_code = self.q._gather_firmware_version()
        self.assertEqual(return_code, 99)

    def test_gather_firmware_version(self):
        self.q.dom0_hwids_info = "BiosVersion: CBET4.13 heads"
        self.q._gather_firmware_version()
        self.assertEqual(self.q.heads_version, "4.13 heads")


if __name__ == '__main__':
    unittest.main()
