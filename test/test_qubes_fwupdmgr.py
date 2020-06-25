#!/usr/bin/python3
import distutils.version as ver
import json
import unittest
import os.path as path
import src.qubes_fwupdmgr as qfwupd
import sys
import io
import platform
from test.fwupd_logs import UPDATE_INFO, GET_DEVICES, DMI_DECODE
from unittest.mock import patch

FWUPD_DOM0_DIR = "/root/.cache/fwupd"
FWUPD_DOM0_UPDATES_DIR = path.join(FWUPD_DOM0_DIR, "updates")
FWUPD_DOM0_UNTRUSTED_DIR = path.join(FWUPD_DOM0_UPDATES_DIR, "untrusted")
FWUPD_DOM0_USBVM_LOG = path.join(FWUPD_DOM0_DIR, "usbvm-devices.log")
FWUPD_DOM0_METADATA_DIR = path.join(FWUPD_DOM0_DIR, "metadata")
FWUPD_DOM0_METADATA_SIGNATURE = path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_DOM0_METADATA_FILE = path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz"
)


def device_connected():
    if 'qubes' not in platform.release():
        return False
    q = qfwupd.QubesFwupdmgr()
    q._get_dom0_devices()
    return "ColorHug2" in q.dom0_devices_info


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
    def test_get_dom0_updates(self):
        self.q._get_dom0_updates()
        self.assertTrue(
            "Devices" in self.q.updates_info,
            msg="Getting available updates failed"
        )

    def test_parse_updates_info(self):
        self.q._parse_updates_info(UPDATE_INFO)
        self.assertEqual(
            self.q.updates_list[0]["Name"],
            "ColorHug2",
            msg="Wrong device name"
        )
        self.assertEqual(
            self.q.updates_list[0]["Version"],
            "2.0.6",
            msg="Wrong update version"
        )
        self.assertEqual(
            self.q.updates_list[0]["Releases"][0]["Url"],
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            msg="Wrong update URL"
        )
        self.assertEqual(
            self.q.updates_list[0]["Releases"][0]["Checksum"],
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96",
            msg="Wrong checksum"
        )

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_download_firmware_updates(self):
        self.q._download_firmware_updates(
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96"
        )
        update_path = path.join(
            FWUPD_DOM0_UPDATES_DIR,
            "0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7"
        )
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
    def test_get_dom0_devices(self):
        self.q._get_dom0_devices()
        self.assertIsNotNone(self.q.dom0_devices_info)

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_get_dom0_devices_qubes(self):
        get_devices_output = io.StringIO()
        sys.stdout = get_devices_output
        self.q.get_devices_qubes()
        self.assertNotEqual(get_devices_output.getvalue().strip(), "")
        sys.stdout = self.captured_output

    @unittest.skipUnless(device_connected(), "Required device not connected")
    def test_get_dom0_updates_qubes(self):
        get_updates_output = io.StringIO()
        sys.stdout = get_updates_output
        self.q.get_updates_qubes()
        self.assertNotEqual(get_updates_output.getvalue().strip(), "")
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

    @unittest.skipUnless(device_connected(), "Required device not connected")
    def test_downgrade_firmware(self):
        old_version = None
        self.q._get_dom0_devices()
        self.q._parse_downgrades(self.q.dom0_devices_info)
        for number, device in enumerate(self.q.downgrades):
            if device["Name"] == "ColorHug2":
                old_version = device["Version"]
                break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1), '1']
        with patch('builtins.input', side_effect=user_input):
            self.q.downgrade_firmware()
        self.q._get_dom0_devices()
        self.q._parse_downgrades(self.q.dom0_devices_info)
        new_version = self.q.downgrades[number]["Version"]
        self.assertTrue(
            ver.LooseVersion(old_version) > ver.LooseVersion(new_version)
        )

    def test_parse_downgrades(self):
        self.q._parse_downgrades(GET_DEVICES)
        self.assertEqual(
            self.q.downgrades[0]["Name"],
            "ColorHug2"
        )
        self.assertEqual(
            self.q.downgrades[0]["Version"],
            "2.0.7"
        )
        self.assertEqual(
            self.q.downgrades[0]["Releases"][0]["Version"],
            "2.0.6"
        )
        self.assertEqual(
            self.q.downgrades[0]["Releases"][0]["Url"],
            "https://fwupd.org/downloads/170f2c19f17b7819644d3fcc7617621cc3350a04-hughski-colorhug2-2.0.6.cab"
        )
        self.assertEqual(
            self.q.downgrades[0]["Releases"][0]["Checksum"],
            "03c9c14db1894a00035ececcfae192865a710e52"
        )

    def test_user_input_downgrade(self):
        user_input = ['1', '6', 'sth', '2.2.1', '', ' ', '\0', '2']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_downgrades(GET_DEVICES)
            device_choice, downgrade_choice = self.q._user_input(
                self.q.downgrades,
                downgrade=True
            )
        self.assertEqual(device_choice, 0)
        self.assertEqual(downgrade_choice, 1)

    def test_user_input_downgrade_N(self):
        user_input = ['N']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_downgrades(GET_DEVICES)
            N_choice = self.q._user_input(
                self.q.downgrades,
                downgrade=True
            )
        self.assertEqual(N_choice, 99)

    @unittest.skipUnless(device_connected(), "Required device not connected")
    def test_update_firmware(self):
        old_version = None
        new_version = None
        self.q._get_dom0_updates()
        self.q._parse_updates_info(self.q.updates_info)
        for number, device in enumerate(self.q.updates_list):
            if device["Name"] == "ColorHug2":
                old_version = device["Version"]
                break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1)]
        with patch('builtins.input', side_effect=user_input):
            self.q.update_firmware()
        self.q._get_dom0_devices()
        dom0_devices_info_dict = json.loads(self.q.dom0_devices_info)
        for device in dom0_devices_info_dict["Devices"]:
            if device["Name"] == "ColorHug2":
                new_version = device["Version"]
                break
        if new_version is None:
            self.fail("Test device not found")
        self.assertTrue(
            ver.LooseVersion(old_version) < ver.LooseVersion(new_version)
        )

    @unittest.skipUnless('qubes' in platform.release(), "requires Qubes OS")
    def test_get_usbvm_devices(self):
        self.q._get_usbvm_devices()
        self.assertTrue(path.exists(FWUPD_DOM0_USBVM_LOG))


if __name__ == '__main__':
    unittest.main()
