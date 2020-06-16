#!/usr/bin/python3
import unittest
import os.path as path
import src.qubes_fwupdmgr as qfwupd
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
                 }"""


class TestQubesFwupdmgr(unittest.TestCase):
    def test_download_metadata(self):
        q = qfwupd.QubesFwupdmgr()
        q.download_metadata()
        self.assertTrue(
                        path.exists(FWUPD_DOM0_METADATA_FILE),
                        msg="Metadata update file does not exist",
                       )
        self.assertTrue(
                        path.exists(FWUPD_DOM0_METADATA_SIGNATURE),
                        msg="Metadata signature does not exist",
                       )

    def test_refresh_metadata(self):
        q = qfwupd.QubesFwupdmgr()
        q.refresh_metadata()
        self.assertEqual(
                         q.output,
                         'Successfully refreshed metadata manually',
                         msg="Metadata refresh failed."
                        )

    def test_get_updates(self):
        q = qfwupd.QubesFwupdmgr()
        q.get_updates()
        self.assertTrue(
                          "Devices" in q.updates_info,
                          msg="Getting available updates failed"
                         )

    def test_parse_updates_info(self):
        q = qfwupd.QubesFwupdmgr()
        q.parse_updates_info(UPDATE_INFO)
        self.assertEqual(
            q.updates_list[0][0],
            "ColorHug2",
            msg="Wrong device name"
        )
        self.assertEqual(
            q.updates_list[0][1],
            "2.0.6",
            msg="Wrong update version"
        )
        self.assertEqual(
            q.updates_list[0][2][1],
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            msg="Wrong update URL"
        )
        self.assertEqual(
            q.updates_list[0][2][2],
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96",
            msg="Wrong checksum"
        )

    def test_download_firmware_updates(self):
        q = qfwupd.QubesFwupdmgr()
        q.download_firmware_updates(
            "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
            "490be5c0b13ca4a3f169bf8bc682ba127b8f7b96"
        )
        update_path = FWUPD_DOM0_UPDATES_DIR + \
            "0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7"
        self.assertTrue(path.exists(update_path))

#   def test_user_input(self):
#       q = qfwupd.QubesFwupdmgr()

if __name__ == '__main__':
    unittest.main()
