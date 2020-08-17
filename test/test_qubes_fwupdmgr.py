#!/usr/bin/python3
import distutils.version as ver
import json
import unittest
import os.path as path
import src.qubes_fwupdmgr as qfwupd
import subprocess
import sys
import io
import platform
from test.fwupd_logs import UPDATE_INFO, GET_DEVICES, DMI_DECODE
from test.fwupd_logs import GET_DEVICES_NO_UPDATES, GET_DEVICES_NO_VERSION
from unittest.mock import patch

FWUPD_DOM0_DIR = "/root/.cache/fwupd"
FWUPD_DOM0_UPDATES_DIR = path.join(FWUPD_DOM0_DIR, "updates")
FWUPD_DOM0_UNTRUSTED_DIR = path.join(FWUPD_DOM0_UPDATES_DIR, "untrusted")
FWUPD_USBVM_LOG = path.join(FWUPD_DOM0_DIR, "usbvm-devices.log")
FWUPD_DOM0_METADATA_DIR = path.join(FWUPD_DOM0_DIR, "metadata")
FWUPD_DOM0_METADATA_SIGNATURE = path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_DOM0_METADATA_FILE = path.join(
    FWUPD_DOM0_METADATA_DIR,
    "firmware.xml.gz"
)
FWUPD_USBVM_DIR = "/home/user/.cache/fwupd"
FWUPD_USBVM_UPDATES_DIR = path.join(FWUPD_USBVM_DIR, "updates")
FWUPD_USBVM_METADATA_DIR = path.join(FWUPD_USBVM_DIR, "metadata")
FWUPD_USBVM_METADATA_SIGNATURE = path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz.asc"
)
FWUPD_USBVM_METADATA_FILE = path.join(
    FWUPD_USBVM_METADATA_DIR,
    "firmware.xml.gz"
)
REQUIRED_DEV = "Requires device not connected"
REQUIRED_USBVM = "Requires sys-usb"
XL_LIST_LOG = "Name                                        ID   Mem VCPUs	State	Time(s)"
USBVM_N = "sys-usb"
FWUPDMGR = "/bin/fwupdmgr"


def check_usbvm():
    """Checks if sys-usb is running"""
    if 'qubes' not in platform.release():
        return False
    q = qfwupd.QubesFwupdmgr()
    q.check_usbvm()
    return "sys-usb" in q.output


def device_connected_dom0():
    """Checks if the testing device is connected in dom0"""
    if 'qubes' not in platform.release():
        return False
    q = qfwupd.QubesFwupdmgr()
    q.check_fwupd_version()
    q._get_dom0_devices()
    return "ColorHug2" in q.dom0_devices_info


def device_connected_usbvm():
    """Checks if the testing device is connected in usbvm"""
    if not check_usbvm():
        return False
    q = qfwupd.QubesFwupdmgr()
    q.check_fwupd_version(usbvm=True)
    q._validate_usbvm_dirs()
    if not path.exists(FWUPD_DOM0_DIR):
        q.refresh_metadata()
    q._get_usbvm_devices()
    with open(FWUPD_USBVM_LOG) as usbvm_device_info:
        return "ColorHug2" in usbvm_device_info.read()


def check_whonix_updatevm():
    """Checks if the sys-whonix is running"""
    if 'qubes' not in platform.release():
        return False
    q = qfwupd.QubesFwupdmgr()
    q.check_usbvm()
    return "sys-whonix" in q.output


class TestQubesFwupdmgr(unittest.TestCase):
    def setUp(self):
        self.q = qfwupd.QubesFwupdmgr()
        self.maxDiff = 2000
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
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

    @unittest.skipUnless(check_whonix_updatevm(), "Requires sys-whonix")
    def test_download_metadata_whonix(self):
        self.q._download_metadata(whonix=True)
        self.assertTrue(
            path.exists(FWUPD_DOM0_METADATA_FILE),
            msg="Metadata update file does not exist",
        )
        self.assertTrue(
            path.exists(FWUPD_DOM0_METADATA_SIGNATURE),
            msg="Metadata signature does not exist",
        )

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_refresh_metadata_dom0(self):
        self.q.refresh_metadata()
        self.assertEqual(
            self.q.output,
            'Successfully refreshed metadata manually\n',
            msg="Metadata refresh failed."
        )

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_refresh_metadata_usbvm(self):
        self.q.refresh_metadata(usbvm=True)
        self.assertEqual(
            self.q.output,
            'Successfully refreshed metadata manually\n',
            msg="Metadata refresh failed."
        )

    @unittest.skipUnless(check_whonix_updatevm(), "Requires sys-whonix")
    def test_refresh_metadata_whonix(self):
        self.q.refresh_metadata(whonix=True)
        self.assertEqual(
            self.q.output,
            'Successfully refreshed metadata manually\n',
            msg="Metadata refresh failed."
        )

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_get_dom0_updates(self):
        self.q.check_fwupd_version()
        self.q._get_dom0_updates()
        self.assertTrue(
            "Devices" in self.q.dom0_updates_info,
            msg="Getting available updates failed"
        )

    def test_parse_updates_info(self):
        self.q._parse_dom0_updates_info(UPDATE_INFO)
        self.assertEqual(
            self.q.dom0_updates_list[0]["Name"],
            "ColorHug2",
            msg="Wrong device name"
        )
        self.assertEqual(
            self.q.dom0_updates_list[0]["Version"],
            "2.0.6",
            msg="Wrong update version"
        )
        self.assertEqual(
            self.q.dom0_updates_list[0]["Releases"][0]["Url"],
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            msg="Wrong update URL"
        )
        self.assertEqual(
            self.q.dom0_updates_list[0]["Releases"][0]["Checksum"],
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96",
            msg="Wrong checksum"
        )

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
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

    @unittest.skipUnless(check_whonix_updatevm(), "Requires sys-whonix")
    def test_download_firmware_updates_whonix(self):
        self.q._download_firmware_updates(
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96",
            whonix=True,
        )
        update_path = path.join(
            FWUPD_DOM0_UPDATES_DIR,
            "0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7"
        )
        self.assertTrue(path.exists(update_path))

    def test_user_input_empty_dict(self):
        downgrade_dict = {
                "usbvm": [],
                "dom0": []
            }
        self.assertEqual(self.q._user_input(downgrade_dict), 99)

    def test_user_input_n(self):
        user_input = ['sth', 'n']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_dom0_updates_info(UPDATE_INFO)
            downgrade_dict = {
                "usbvm": self.q.dom0_updates_list,
                "dom0": self.q.dom0_updates_list
            }
            choice = self.q._user_input(
                downgrade_dict,
                usbvm=True
            )
        self.assertEqual(choice, 99)
        user_input = ['sth', 'N']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_dom0_updates_info(UPDATE_INFO)
            downgrade_dict = {
                "usbvm": self.q.dom0_updates_list,
                "dom0": self.q.dom0_updates_list
            }
            choice = self.q._user_input(
                downgrade_dict,
                usbvm=True
            )
        self.assertEqual(choice, 99)

    def test_user_input_choice(self):
        user_input = ['6', '1']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_dom0_updates_info(UPDATE_INFO)
            updates_dict = {
                "usbvm": self.q.dom0_updates_list,
                "dom0": self.q.dom0_updates_list
            }
            key, choice = self.q._user_input(updates_dict)
        self.assertEqual(key, "dom0")
        self.assertEqual(choice, 0)

    def test_user_input_choice_usbvm(self):
        user_input = ['6', '2']
        with patch('builtins.input', side_effect=user_input):
            self.q._parse_dom0_updates_info(UPDATE_INFO)
            updates_dict = {
                "usbvm": self.q.dom0_updates_list,
                "dom0": self.q.dom0_updates_list
            }
            key, choice = self.q._user_input(updates_dict, usbvm=True)
        self.assertEqual(key, "usbvm")
        self.assertEqual(choice, 0)

    def test_parse_parameters(self):
        self.q._parse_dom0_updates_info(UPDATE_INFO)
        update_dict = {"dom0": self.q.dom0_updates_list}
        self.q._parse_parameters(update_dict, "dom0", 0)
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

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_clean_cache_dom0(self):
        self.q.clean_cache()
        self.assertFalse(path.exists(FWUPD_DOM0_METADATA_DIR))
        self.assertFalse(path.exists(FWUPD_DOM0_UNTRUSTED_DIR))

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_clean_cache_dom0_n_usbvm(self):
        self.q._validate_usbvm_dirs()
        self.q.clean_cache(usbvm=True)
        self.assertFalse(path.exists(FWUPD_DOM0_METADATA_DIR))
        self.assertFalse(path.exists(FWUPD_DOM0_UNTRUSTED_DIR))
        cmd_validate_metadata = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"! [ -d {FWUPD_USBVM_METADATA_DIR} ]"
        ]
        p = subprocess.Popen(cmd_validate_metadata)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Creating metadata directory failed"
        )
        cmd_validate_udpdate = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"! [ -d {FWUPD_USBVM_UPDATES_DIR} ]"
        ]
        p = subprocess.Popen(cmd_validate_udpdate)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Cleaning update directory failed"
        )

    def test_output_crawler(self):
        crawler_output = io.StringIO()
        sys.stdout = crawler_output
        self.q._output_crawler(json.loads(UPDATE_INFO), 0)
        with open("test/logs/get_devices.log", "r") as get_devices:
            self.assertEqual(
                get_devices.read(),
                crawler_output.getvalue().strip()
            )
        sys.stdout = self.captured_output

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_get_dom0_devices(self):
        self.q.check_fwupd_version()
        self.q._get_dom0_devices()
        self.assertIsNotNone(self.q.dom0_devices_info)

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_get_devices_qubes_dom0(self):
        get_devices_output = io.StringIO()
        sys.stdout = get_devices_output
        self.q.check_fwupd_version()
        self.q.get_devices_qubes()
        self.assertNotEqual(get_devices_output.getvalue().strip(), "")
        sys.stdout = self.captured_output

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_get_devices_qubes_usbvm(self):
        get_devices_output = io.StringIO()
        sys.stdout = get_devices_output
        self.q.check_fwupd_version(usbvm=True)
        self.q.get_devices_qubes(usbvm=True)
        self.assertNotEqual(get_devices_output.getvalue().strip(), "")
        sys.stdout = self.captured_output

    @unittest.skipUnless(device_connected_dom0(), REQUIRED_DEV)
    def test_get_updates_qubes_dom0(self):
        get_updates_output = io.StringIO()
        sys.stdout = get_updates_output
        self.q.check_fwupd_version()
        self.q.get_updates_qubes()
        self.assertNotEqual(get_updates_output.getvalue().strip(), "")
        sys.stdout = self.captured_output

    @unittest.skipUnless(device_connected_usbvm(), REQUIRED_DEV)
    def test_get_updates_qubes_usbvm(self):
        get_updates_output = io.StringIO()
        sys.stdout = get_updates_output
        self.q.check_fwupd_version(usbvm=True)
        self.q.get_updates_qubes(usbvm=True)
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
        self.q.dmi_version = "P.1.0"
        self.q._verify_dmi("test/logs/", "P1.1")

    @patch(
        'src.qubes_fwupdmgr.QubesFwupdmgr._read_dmi',
        return_value=DMI_DECODE
    )
    def test_verify_dmi_wrong_vendor(self, output):
        with self.assertRaises(ValueError) as wrong_vendor:
            self.q.dmi_version = "P.1.0"
            self.q._verify_dmi("test/logs/metainfo_name/", "P1.1")
        self.assertTrue(
            "Wrong firmware provider." in str(wrong_vendor.exception)
        )

    @patch(
        'src.qubes_fwupdmgr.QubesFwupdmgr._read_dmi',
        return_value=DMI_DECODE
    )
    def test_verify_dmi_version(self, output):
        self.q.dmi_version = "P1.0"
        with self.assertRaises(ValueError) as downgrade:
            self.q._verify_dmi("test/logs/metainfo_version/", "P0.1")
        self.assertTrue(
            "P0.1 < P1.0 Downgrade not allowed" in str(downgrade.exception)
        )

    @unittest.skipUnless(device_connected_dom0(), REQUIRED_DEV)
    def test_downgrade_firmware_dom0(self):
        old_version = None
        self.q.check_fwupd_version()
        self.q._get_dom0_devices()
        downgrades = self.q._parse_downgrades(self.q.dom0_devices_info)
        for number, device in enumerate(downgrades):
            if "Name" not in device:
                continue
            if device["Name"] == "ColorHug2":
                old_version = device["Version"]
                break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1), '1']
        with patch('builtins.input', side_effect=user_input):
            self.q.downgrade_firmware()
        self.q._get_dom0_devices()
        downgrades = self.q._parse_downgrades(self.q.dom0_devices_info)
        new_version = downgrades[number]["Version"]
        self.assertTrue(
            ver.LooseVersion(old_version) > ver.LooseVersion(new_version)
        )

    @unittest.skipUnless(check_whonix_updatevm(), REQUIRED_DEV)
    def test_update_n_downgrade_firmware_whonix(self):
        old_version = None
        self.q.check_fwupd_version(usbvm=True)
        self.q._get_dom0_devices()
        dom0_downgrades = self.q._parse_downgrades(self.q.dom0_devices_info)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            downgrades = self.q._parse_downgrades(usbvm_device_info.read())
            for number, device in enumerate(downgrades):
                if "Name" not in device:
                    continue
                if device["Name"] == "ColorHug2":
                    old_version = device["Version"]
                    break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1+len(dom0_downgrades)), '1']
        with patch('builtins.input', side_effect=user_input):
            self.q.downgrade_firmware(usbvm=True, whonix=True)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            downgrades = self.q._parse_downgrades(usbvm_device_info.read())
        new_version = downgrades[number]["Version"]
        self.assertTrue(
            ver.LooseVersion(old_version) > ver.LooseVersion(new_version)
        )
        old_version = None
        new_version = None
        self.q.check_fwupd_version(usbvm=True)
        self.q._get_dom0_updates()
        self.q._parse_dom0_updates_info(self.q.dom0_updates_info)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            self.q._parse_usbvm_updates(usbvm_device_info.read())
            for number, device in enumerate(self.q.usbvm_updates_list):
                if "Name" not in device:
                    continue
                if device["Name"] == "ColorHug2":
                    old_version = device["Version"]
                    break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1+len(self.q.dom0_updates_list)), '1']
        with patch('builtins.input', side_effect=user_input):
            self.q.update_firmware(usbvm=True, whonix=True)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            usbvm_devices_info_dict = json.loads(usbvm_device_info.read())
        for device in usbvm_devices_info_dict["Devices"]:
            if "Name" not in device:
                continue
            if device["Name"] == "ColorHug2":
                new_version = device["Version"]
                break
        if new_version is None:
            self.fail("Test device not found")
        self.assertTrue(
            ver.LooseVersion(old_version) < ver.LooseVersion(new_version)
        )

    @unittest.skipUnless(device_connected_usbvm(), REQUIRED_DEV)
    def test_downgrade_firmware_usbvm(self):
        old_version = None
        self.q.check_fwupd_version(usbvm=True)
        self.q._get_dom0_devices()
        dom0_downgrades = self.q._parse_downgrades(self.q.dom0_devices_info)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            downgrades = self.q._parse_downgrades(usbvm_device_info.read())
            for number, device in enumerate(downgrades):
                if "Name" not in device:
                    continue
                if device["Name"] == "ColorHug2":
                    old_version = device["Version"]
                    break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1+len(dom0_downgrades)), '1']
        with patch('builtins.input', side_effect=user_input):
            self.q.downgrade_firmware(usbvm=True)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            downgrades = self.q._parse_downgrades(usbvm_device_info.read())
        new_version = downgrades[number]["Version"]
        self.assertTrue(
            ver.LooseVersion(old_version) > ver.LooseVersion(new_version)
        )

    def test_parse_downgrades(self):
        downgrades = self.q._parse_downgrades(GET_DEVICES)
        self.assertEqual(
            downgrades[0]["Name"],
            "ColorHug2"
        )
        self.assertEqual(
            downgrades[0]["Version"],
            "2.0.6"
        )
        self.assertEqual(
            downgrades[0]["Releases"][0]["Version"],
            "2.0.5"
        )
        self.assertEqual(
            downgrades[0]["Releases"][0]["Url"],
            "https://fwupd.org/downloads/f7dd4ab29fa610438571b8b62b26b0b0e57bb35b-hughski-colorhug2-2.0.5.cab"
        )
        self.assertEqual(
            downgrades[0]["Releases"][0]["Checksum"],
            "4ee9dfa38df3b810f739d8a19d13da1b3175fb87"
        )

    def test_parse_downgrades_no_version(self):
        downgrades = self.q._parse_downgrades(GET_DEVICES_NO_VERSION)
        self.assertEqual(
            downgrades[0]["Name"],
            "ColorHug2"
        )
        self.assertEqual(
            downgrades[0]["Version"],
            "2.0.6"
        )
        self.assertEqual(
            downgrades[0]["Releases"][0]["Version"],
            "2.0.5"
        )
        self.assertEqual(
            downgrades[0]["Releases"][0]["Url"],
            "https://fwupd.org/downloads/f7dd4ab29fa610438571b8b62b26b0b0e57bb35b-hughski-colorhug2-2.0.5.cab"
        )
        self.assertEqual(
            downgrades[0]["Releases"][0]["Checksum"],
            "4ee9dfa38df3b810f739d8a19d13da1b3175fb87"
        )

    def test_user_input_downgrade_usbvm(self):
        user_input = ['2', '6', 'sth', '2.2.1', '', ' ', '\0', '2']
        with patch('builtins.input', side_effect=user_input):
            downgrade_list = self.q._parse_downgrades(GET_DEVICES)
            downgrade_dict = {
                "usbvm": downgrade_list,
                "dom0": downgrade_list
            }
            key, device_choice, downgrade_choice = self.q._user_input(
                downgrade_dict,
                downgrade=True,
                usbvm=True
            )
        self.assertEqual(key, "usbvm")
        self.assertEqual(device_choice, 0)
        self.assertEqual(downgrade_choice, 1)

    def test_user_input_downgrade_dom0(self):
        user_input = ['1', '6', 'sth', '2.2.1', '', ' ', '\0', '2']
        with patch('builtins.input', side_effect=user_input):
            downgrade_list = self.q._parse_downgrades(GET_DEVICES)
            downgrade_dict = {
                "dom0": downgrade_list
            }
            key, device_choice, downgrade_choice = self.q._user_input(
                downgrade_dict,
                downgrade=True,
            )
        self.assertEqual(key, "dom0")
        self.assertEqual(device_choice, 0)
        self.assertEqual(downgrade_choice, 1)

    def test_user_input_downgrade_N(self):
        user_input = ['N']
        with patch('builtins.input', side_effect=user_input):
            downgrade_list = self.q._parse_downgrades(GET_DEVICES)
            downgrade_dict = {
                "usbvm": downgrade_list,
                "dom0": downgrade_list
            }
            N_choice = self.q._user_input(
                downgrade_dict,
                downgrade=True,
                usbvm=True
            )
        self.assertEqual(N_choice, 99)

    @unittest.skipUnless(device_connected_dom0(), REQUIRED_DEV)
    def test_update_firmware_dom0(self):
        old_version = None
        new_version = None
        self.q.check_fwupd_version()
        self.q._get_dom0_updates()
        self.q._parse_dom0_updates_info(self.q.dom0_updates_info)
        for number, device in enumerate(self.q.dom0_updates_list):
            if "Name" not in device:
                continue
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
            if "Name" not in device:
                continue
            if device["Name"] == "ColorHug2":
                new_version = device["Version"]
                break
        if new_version is None:
            self.fail("Test device not found")
        self.assertTrue(
            ver.LooseVersion(old_version) < ver.LooseVersion(new_version)
        )

    @unittest.skipUnless(device_connected_usbvm(), REQUIRED_DEV)
    def test_update_firmware_usbvm(self):
        old_version = None
        new_version = None
        self.q.check_fwupd_version(usbvm=True)
        self.q._get_dom0_updates()
        self.q._parse_dom0_updates_info(self.q.dom0_updates_info)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            self.q._parse_usbvm_updates(usbvm_device_info.read())
            for number, device in enumerate(self.q.usbvm_updates_list):
                if "Name" not in device:
                    continue
                if device["Name"] == "ColorHug2":
                    old_version = device["Version"]
                    break
        if old_version is None:
            self.fail("Test device not found")
        user_input = [str(number+1+len(self.q.dom0_updates_list)), '1']
        with patch('builtins.input', side_effect=user_input):
            self.q.update_firmware(usbvm=True)
        self.q._get_usbvm_devices()
        with open(FWUPD_USBVM_LOG) as usbvm_device_info:
            usbvm_devices_info_dict = json.loads(usbvm_device_info.read())
        for device in usbvm_devices_info_dict["Devices"]:
            if "Name" not in device:
                continue
            if device["Name"] == "ColorHug2":
                new_version = device["Version"]
                break
        if new_version is None:
            self.fail("Test device not found")
        self.assertTrue(
            ver.LooseVersion(old_version) < ver.LooseVersion(new_version)
        )

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_get_usbvm_devices(self):
        self.q.check_fwupd_version(usbvm=True)
        self.q._get_usbvm_devices()
        self.assertTrue(path.exists(FWUPD_USBVM_LOG))

    def test_parse_usbvm_updates(self):
        self.q._parse_usbvm_updates(GET_DEVICES)
        self.assertEqual(self.q.usbvm_updates_list[0]["Name"], "ColorHug2")
        self.assertEqual(self.q.usbvm_updates_list[0]["Version"], "2.0.6")
        self.assertListEqual(
            self.q.usbvm_updates_list[0]["Releases"],
            [
                {
                    'Checksum': '490be5c0b13ca4a3f169bf8bc682ba127b8f7b96',
                    'Description': '<p>This release fixes prevents the firmware returning an '
                                   'error when the remote SHA1 hash was never sent.</p>',
                    'Url': 'https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab',
                    'Version': '2.0.7'
                }
            ]
        )

    def test_parse_usbvm_updates_no_updates_available(self):
        self.q._parse_usbvm_updates(GET_DEVICES_NO_UPDATES)
        self.assertListEqual(self.q.usbvm_updates_list, [])

    def test_updates_crawler(self):
        crawler_output = io.StringIO()
        sys.stdout = crawler_output
        self.q._parse_usbvm_updates(GET_DEVICES)
        self.q._updates_crawler(self.q.usbvm_updates_list, usbvm=True)
        with open("test/logs/get_updates.log", "r") as getupdates:
            self.assertEqual(
                getupdates.read(),
                crawler_output.getvalue().strip()
            )
        sys.stdout = self.captured_output

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_validate_usbvm_dirs(self):
        self.q._validate_usbvm_dirs()
        cmd_validate_metadata = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"[ -d {FWUPD_USBVM_METADATA_DIR} ]"
        ]
        p = subprocess.Popen(cmd_validate_metadata)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Creating metadata directory failed"
        )
        cmd_validate_udpdate = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"[ -d {FWUPD_USBVM_UPDATES_DIR} ]"
        ]
        p = subprocess.Popen(cmd_validate_udpdate)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Creating update directory failed"
        )

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_copy_usbvm_metadata(self):
        self.q._download_metadata()
        self.q._validate_usbvm_dirs()
        self.q._copy_usbvm_metadata()
        cmd_validate_metadata_file = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"[ -f {FWUPD_USBVM_METADATA_FILE} ]"
        ]
        p = subprocess.Popen(cmd_validate_metadata_file)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Metadata file does not exist"
        )
        cmd_validate_metadata_sig = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"[ -f {FWUPD_USBVM_METADATA_SIGNATURE} ]"
        ]
        p = subprocess.Popen(cmd_validate_metadata_sig)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Metadata signature does not exist"
        )

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_validate_usbvm_metadata(self):
        self.q._download_metadata()
        self.q._validate_usbvm_dirs()
        self.q._copy_usbvm_metadata()
        self.q._validate_usbvm_metadata()

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_refresh_usbvm_metadata(self):
        self.q._download_metadata()
        self.q._validate_usbvm_dirs()
        self.q._copy_usbvm_metadata()
        self.q._validate_usbvm_metadata()
        self.q._refresh_usbvm_metadata()

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_clean_usbvm(self):
        self.q._validate_usbvm_dirs()
        self.q._clean_usbvm()
        cmd_validate_metadata = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"! [ -d {FWUPD_USBVM_METADATA_DIR} ]"
        ]
        p = subprocess.Popen(cmd_validate_metadata)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Cleaning metadata directory failed"
        )
        cmd_validate_udpdate = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            f"! [ -d {FWUPD_USBVM_METADATA_DIR} ]"
        ]
        p = subprocess.Popen(cmd_validate_udpdate)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Cleaning update directory failed"
        )

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_validate_usbvm_archive(self):
        url = "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab"
        sha = "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96"
        name = url.replace("https://fwupd.org/downloads/", "")
        self.q._clean_usbvm()
        self.q._validate_usbvm_dirs()
        self.q._download_firmware_updates(
            url,
            sha
        )
        self.q._copy_firmware_updates(
            name
        )
        self.q._validate_usbvm_archive(
            name,
            sha
        )
        cmd_validate_udpdate = [
            "qvm-run",
            "--pass-io",
            "sys-usb",
            "[ -d %s ]" %
            path.join(FWUPD_USBVM_UPDATES_DIR, name.replace(".cab", ""))
        ]
        p = subprocess.Popen(cmd_validate_udpdate)
        p.wait()
        self.assertEqual(
            p.returncode,
            0,
            msg="Archive validation failed"
        )

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_check_usbvm(self):
        self.q.check_usbvm()
        self.assertTrue(XL_LIST_LOG in self.q.output)

    @unittest.skipUnless('qubes' in platform.release(), "Requires Qubes OS")
    def test_check_fwupd_version_dom0(self):
        self.q.check_fwupd_version()
        version_check = 'client version:\t1.3.8'
        cmd_version = [
            "fwupdmgr",
            "--version"
        ]
        p = subprocess.Popen(
            cmd_version,
            stdout=subprocess.PIPE
        )
        client_version = p.communicate()[0].decode().split("\n")[0]
        if ver.LooseVersion(version_check) > ver.LooseVersion(client_version):
            self.assertEqual(
                self.q.fwupdagent_usbvm,
                "/usr/libexec/fwupd/fwupdagent"
            )
        else:
            self.assertEqual(self.q.fwupdagent_dom0, "/bin/fwupdagent")

    @unittest.skipUnless(check_usbvm(), REQUIRED_USBVM)
    def test_check_fwupd_version_usbvm(self):
        self.q.check_fwupd_version(usbvm=True)
        version_check = 'client version:\t1.3.8'
        cmd_version = f'"{FWUPDMGR}" --version'
        cmd_usbvm_version = [
            'qvm-run',
            '--pass-io',
            USBVM_N,
            cmd_version
        ]
        p = subprocess.Popen(
            cmd_usbvm_version,
            stdout=subprocess.PIPE
        )
        client_version = p.communicate()[0].decode().split("\n")[0]
        if ver.LooseVersion(version_check) > ver.LooseVersion(client_version):
            self.assertEqual(
                self.q.fwupdagent_usbvm,
                "/usr/libexec/fwupd/fwupdagent"
            )
        else:
            self.assertEqual(self.q.fwupdagent_usbvm, "/bin/fwupdagent")


if __name__ == '__main__':
    unittest.main()
