#!/usr/bin/python3
import json
import unittest
import os.path as path
import src.qubes_fwupdmgr as qfwupd
import sys
import io
import platform
from unittest.mock import patch

FWUPD_DOM0_DIR = "/root/.cache/fwupd/"
FWUPD_DOM0_METADATA_DIR = FWUPD_DOM0_DIR + "metadata/"
FWUPD_DOM0_METADATA_SIGNATURE = FWUPD_DOM0_METADATA_DIR + "firmware.xml.gz.asc"
FWUPD_DOM0_METADATA_FILE = FWUPD_DOM0_METADATA_DIR + "firmware.xml.gz"
FWUPD_DOM0_UPDATES_DIR = FWUPD_DOM0_DIR + "updates/"
FWUPD_DOM0_UNTRUSTED_DIR = FWUPD_DOM0_UPDATES_DIR + "untrusted/"

UPDATE_INFO = """{
                  "Devices" : [
                     {
                       "Name" : "ColorHug2",
                       "DeviceId" : "cf294bf55b333004beb7c41f952c1838c23e1f4a",
                       "Guid" : [
                         "2082b5e0-7a64-478a-b1b2-e3404fab6dad",
                         "aa4b4156-9732-55db-9500-bf6388508ee3",
                         "101ee86a-7bea-59fb-9f89-6b6297ceed3b",
                         "2fa8891f-3ece-53a4-adc4-0dd875685f30"
                       ],
                       "Summary" : "An open source display colorimeter",
                       "Plugin" : "colorhug",
                       "Protocol" : "com.hughski.colorhug",
                       "Flags" : [
                         "updatable",
                         "supported",
                         "registered",
                         "self-recovery"
                       ],
                       "Vendor" : "Hughski Ltd.",
                       "VendorId" : "USB:0x273F",
                       "Version" : "2.0.6",
                       "VersionFormat" : "triplet",
                       "Icons" : [
                         "colorimeter-colorhug"
                       ],
                       "InstallDuration" : 8,
                       "Created" : 1592310848,
                       "Releases" : [
                         {
                           "AppstreamId" : "com.hughski.ColorHug2.firmware",
                           "RemoteId" : "lvfs",
                           "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                           "Description" : "<p>This release fixes prevents the firmware returning an error when the remote SHA1 hash was never sent.</p>",
                           "Version" : "2.0.7",
                           "Filename" : "658851e6f27c4d87de19cd66b97b610d100efe09",
                           "Protocol" : "com.hughski.colorhug",
                           "Checksum" : [
                             "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96"
                           ],
                           "License" : "GPL-2.0+",
                           "Size" : 16384,
                           "Uri" : "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
                           "Homepage" : "http://www.hughski.com/",
                           "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                           "Vendor" : "Hughski Limited",
                           "Flags" : [
                             "is-upgrade"
                           ],
                           "InstallDuration" : 8
                         }
                       ]
                     }
                   ]
                 }
"""

DMI_DECODE ="""# dmidecode 3.1
Getting SMBIOS data from sysfs.
SMBIOS 3.1.1 present.

Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
    Vendor: Dell Inc.
    Version: P1.00
    Release Date: 02/09/2018
    Address: 0xF0000
    Runtime Size: 64 kB
    ROM Size: 16 MB
    Characteristics:
        PCI is supported
        BIOS is upgradeable
        BIOS shadowing is allowed
        Boot from CD is supported
        Selectable boot is supported
        BIOS ROM is socketed
        EDD is supported
        5.25"/1.2 MB floppy services are supported (int 13h)
        3.5"/720 kB floppy services are supported (int 13h)
        3.5"/2.88 MB floppy services are supported (int 13h)
        Print screen service is supported (int 5h)
        8042 keyboard services are supported (int 9h)
        Serial services are supported (int 14h)
        Printer services are supported (int 17h)
        ACPI is supportedUSB legacy is supported
        BIOS boot specification is supported
        Targeted content distribution is supported
        UEFI is supported
    BIOS Revision: 5.13
"""


class TestQubesFwupdmgr(unittest.TestCase):
    def setUp(self):
        self.q = qfwupd.QubesFwupdmgr()
        self.maxDiff = 1500
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_download_metadata(self):
        self.q._download_metadata()
        self.assertTrue(
            path.exists(FWUPD_DOM0_METADATA_FILE),
            msg="Metadata update file does not exist",
        )
        self.assertTrue(
            path.exists(FWUPD_DOM0_METADATA_SIGNATURE),
            msg="Metadata signature does not exist",
        )

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_refresh_metadata(self):
        self.q.refresh_metadata()
        self.assertEqual(
            self.q.output,
            'Successfully refreshed metadata manually\n',
            msg="Metadata refresh failed."
        )

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_get_updates(self):
        self.q._get_updates()
        self.assertTrue(
            "Devices" in self.q.updates_info,
            msg="Getting available updates failed"
        )

    def test_parse_updates_info(self):
        self.q._parse_updates_info(UPDATE_INFO)
        self.assertEqual(
            self.q.updates_list[0][0],
            "ColorHug2",
            msg="Wrong device name"
        )
        self.assertEqual(
            self.q.updates_list[0][1],
            "2.0.6",
            msg="Wrong update version"
        )
        self.assertEqual(
            self.q.updates_list[0][2][0][1],
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            msg="Wrong update URL"
        )
        self.assertEqual(
            self.q.updates_list[0][2][0][2],
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96",
            msg="Wrong checksum"
        )

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_download_firmware_updates(self):
        self.q._download_firmware_updates(
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96"
        )
        update_path = FWUPD_DOM0_UPDATES_DIR + \
            "0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7"
        self.assertTrue(path.exists(update_path))

    def test_user_input_empty_list(self):
        empty_update_list = []
        self.assertEqual(self.q._user_input(empty_update_list), 99)

    def test_user_input_n(self):
        user_input = ['sth', 'n']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_updates_info(UPDATE_INFO)
            choice = self.q._user_input(self.q.updates_list)
        self.assertEqual(choice, 99)
        user_input = ['sth', 'N']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_updates_info(UPDATE_INFO)
            choice = self.q._user_input(self.q.updates_list)
        self.assertEqual(choice, 99)

    def test_user_input_choice(self):
        user_input = ['6', '1']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_updates_info(UPDATE_INFO)
            choice = self.q._user_input(self.q.updates_list)
        self.assertEqual(choice, 0)

    def test_parse_parameters(self):
        self.q._parse_updates_info(UPDATE_INFO)
        self.q._parse_parameters(self.q.updates_list, 0)
        self.assertEqual(
            self.q.url,
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab"
        )
        self.assertEqual(
            self.q.sha,
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96"
        )
        self.assertEqual(
            self.q.version,
            "2.0.7"
        )

    def test_clean_cache(self):
        self.q.clean_cache()
        self.assertFalse(path.exists(FWUPD_DOM0_METADATA_DIR))
        self.assertFalse(path.exists(FWUPD_DOM0_UNTRUSTED_DIR))

    def test_output_crawler(self):
        crawler_output = io.StringIO()
        sys.stdout = crawler_output
        self.q._output_crawler(json.loads(UPDATE_INFO), 0)
        sys.stdout = sys.__stdout__
        with open("test/logs/getupdates.log", "r") as getupdates:
            self.assertEqual(
                getupdates.read(),
                crawler_output.getvalue().strip()
            )
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_get_devices(self):
        self.q._get_devices()
        self.assertIsNotNone(self.q.devices_info)

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_get_devices_qubes(self):
        get_devices_output = io.StringIO()
        sys.stdout = get_devices_output
        self.q.get_devices_qubes()
        self.assertNotEqual(get_devices_output.getvalue().strip(), "")
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_get_updates_qubes(self):
        get_devices_output = io.StringIO()
        sys.stdout = get_devices_output
        self.q.get_devices_qubes()
        self.assertNotEqual(get_devices_output.getvalue().strip(), "")
        sys.stdout = self.captured_output

    def test_help(self):
        help_output = io.StringIO()
        sys.stdout = help_output
        self.q.help()
        with open("test/logs/help.log", "r") as help_log:
            self.assertEqual(
                help_log.read(),
                help_output.getvalue().strip()
            )
        sys.stdout = self.captured_output

    @patch(
        'src.qubes_fwupdmgr.QubesFwupdmgr._read_dmi',
        return_value=DMI_DECODE
    )
    def test_verify_dmi(self, output):
        self.q._verify_dmi("test/logs/", "P1.1")

    @patch(
        'src.qubes_fwupdmgr.QubesFwupdmgr._read_dmi',
        return_value=DMI_DECODE
    )
    def test_verify_dmi_wrong_vendor(self, output):
        with self.assertRaises(ValueError) as wrong_vendor:
            self.q._verify_dmi("test/logs/metainfo_name/", "P1.1")
        self.assertTrue(
            "Wrong firmware provider." in str(wrong_vendor.exception)
        )

    @patch(
        'src.qubes_fwupdmgr.QubesFwupdmgr._read_dmi',
        return_value=DMI_DECODE
    )
    def test_verify_dmi_argument_version(self, output):
        with self.assertRaises(ValueError) as argument_version:
            self.q._verify_dmi("test/logs/", "P1.0")
        self.assertTrue(
            "Wrong firmware version." in str(argument_version.exception)
        )

    @patch(
        'src.qubes_fwupdmgr.QubesFwupdmgr._read_dmi',
        return_value=DMI_DECODE
    )
    def test_verify_dmi_version(self, output):
        with self.assertRaises(ValueError) as downgrade:
            self.q._verify_dmi("test/logs/metainfo_version/", "P0.1")
        self.assertTrue(
            "P0.1 < P1.00 Downgrade not allowed" in str(downgrade.exception)
        )


if __name__ == '__main__':
    unittest.main()
