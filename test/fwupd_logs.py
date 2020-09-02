#!/usr/bin/python3

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

DMI_DECODE = """# dmidecode 3.1
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

GET_DEVICES = """{
    "Devices" : [
        {
            "Name" : "ColorHug2",
            "DeviceId" : "203f56e4e186d078ce76725e708400aafc253aac",
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
                "self-recovery",
                "add-counterpart-guids"
            ],
            "Vendor" : "Hughski Ltd.",
            "VendorId" : "USB:0x273F",
            "Version" : "2.0.6",
            "VersionFormat" : "triplet",
            "Icons" : [
                "colorimeter-colorhug"
            ],
            "InstallDuration" : 8,
            "Created" : 1592916092,
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
                    "Created" : 1482901200,
                    "Uri" : "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on the second half of batch 16</li><li>Fix the firmware upgrade process using new versions of fwupd</li></ul>",
                    "Version" : "2.0.6",
                    "Filename" : "f038b5ca40e6d7c1c0299a9e1dcc129d5f6371b6",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "03c9c14db1894a00035ececcfae192865a710e52"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1450792062,
                    "Uri" : "https://fwupd.org/downloads/170f2c19f17b7819644d3fcc7617621cc3350a04-hughski-colorhug2-2.0.6.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on batch 16</li><li>Make the self test more sensitive to detect floating pins</li></ul>",
                    "Version" : "2.0.5",
                    "Filename" : "ae76c6b704b60f9d1d88dc2c8ec8a62d7b2331dc",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "4ee9dfa38df3b810f739d8a19d13da1b3175fb87"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1444059405,
                    "Uri" : "https://fwupd.org/downloads/f7dd4ab29fa610438571b8b62b26b0b0e57bb35b-hughski-colorhug2-2.0.5.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This unstable release adds the following features:</p><ul><li>Add TakeReadingArray to enable panel latency measurements</li><li>Speed up the auto-scaled measurements considerably, using 256ms as the smallest sample duration</li></ul>",
                    "Version" : "2.0.2",
                    "Filename" : "d4b3144daeb2418634f9d464d88d55590bcd9ac7",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "448527af3ce019d03dbb77aaebaa7eb893f1ea20"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 15680,
                    "Created" : 1416675439,
                    "Uri" : "https://fwupd.org/downloads/30a121f26c039745aeb5585252d4a9b5386d71cb-hughski-colorhug2-2.0.2.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                }
            ]
        },
        {
            "Name" : "GP106 [GeForce GTX 1060 6GB]",
            "DeviceId" : "71b677ca0f1bc2c5b804fa1d59e52064ce589293",
            "Guid" : [
                "b080a9ba-fff8-5de0-b641-26f782949f94",
                "f95bfce3-18e4-58b0-bd81-136457521383"
            ],
            "Plugin" : "optionrom",
            "Flags" : [
                "internal",
                "registered",
                "can-verify",
                "can-verify-image"
            ],
            "Vendor" : "NVIDIA Corporation",
            "VendorId" : "PCI:0x10DE",
            "Version" : "a1",
            "VersionFormat" : "plain",
            "Icons" : [
                "audio-card"
            ],
            "Created" : 1592899254
        },
        {
            "Name" : "Intel(R) Core™ i5-8400 CPU @ 2.80GHz",
            "DeviceId" : "4bde70ba4e39b28f9eab1628f9dd6e6244c03027",
            "Guid" : [
                "b9a2dd81-159e-5537-a7db-e7101d164d3f"
            ],
            "Plugin" : "cpu",
            "Flags" : [
                "internal",
                "registered"
            ],
            "Vendor" : "GenuineIntel",
            "Version" : "0xd6",
            "VersionFormat" : "hex",
            "Icons" : [
                "computer"
            ],
            "Created" : 1592899249
        },
        {
            "Name" : "SSDPR-CX400-256",
            "DeviceId" : "948241a24320627284597ec95079cc1341c90518",
            "Guid" : [
                "09fa3842-45bc-5226-a8ec-1668fc61f88f",
                "57d6b2ff-710d-5cd2-98be-4f6b8b7c5287",
                "36bebd37-b680-5d56-83a1-6693033d4098"
            ],
            "Summary" : "ATA Drive",
            "Plugin" : "ata",
            "Protocol" : "org.t13.ata",
            "Flags" : [
                "internal",
                "updatable",
                "require-ac",
                "registered",
                "needs-reboot",
                "usable-during-update"
            ],
            "Vendor" : "Phison",
            "VendorId" : "ATA:0x1987",
            "Version" : "SBFM61.3",
            "VersionFormat" : "plain",
            "Icons" : [
                "drive-harddisk"
            ],
            "Created" : 1592899254
        }
    ]
}
"""

GET_DEVICES_NO_UPDATES = """{
    "Devices" : [
        {
            "Name" : "ColorHug2",
            "DeviceId" : "203f56e4e186d078ce76725e708400aafc253aac",
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
                "self-recovery",
                "add-counterpart-guids"
            ],
            "Vendor" : "Hughski Ltd.",
            "VendorId" : "USB:0x273F",
            "Version" : "2.0.7",
            "VersionFormat" : "triplet",
            "Icons" : [
                "colorimeter-colorhug"
            ],
            "InstallDuration" : 8,
            "Created" : 1592916092,
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
                    "Created" : 1482901200,
                    "Uri" : "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on the second half of batch 16</li><li>Fix the firmware upgrade process using new versions of fwupd</li></ul>",
                    "Version" : "2.0.6",
                    "Filename" : "f038b5ca40e6d7c1c0299a9e1dcc129d5f6371b6",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "03c9c14db1894a00035ececcfae192865a710e52"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1450792062,
                    "Uri" : "https://fwupd.org/downloads/170f2c19f17b7819644d3fcc7617621cc3350a04-hughski-colorhug2-2.0.6.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on batch 16</li><li>Make the self test more sensitive to detect floating pins</li></ul>",
                    "Version" : "2.0.5",
                    "Filename" : "ae76c6b704b60f9d1d88dc2c8ec8a62d7b2331dc",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "4ee9dfa38df3b810f739d8a19d13da1b3175fb87"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1444059405,
                    "Uri" : "https://fwupd.org/downloads/f7dd4ab29fa610438571b8b62b26b0b0e57bb35b-hughski-colorhug2-2.0.5.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This unstable release adds the following features:</p><ul><li>Add TakeReadingArray to enable panel latency measurements</li><li>Speed up the auto-scaled measurements considerably, using 256ms as the smallest sample duration</li></ul>",
                    "Version" : "2.0.2",
                    "Filename" : "d4b3144daeb2418634f9d464d88d55590bcd9ac7",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "448527af3ce019d03dbb77aaebaa7eb893f1ea20"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 15680,
                    "Created" : 1416675439,
                    "Uri" : "https://fwupd.org/downloads/30a121f26c039745aeb5585252d4a9b5386d71cb-hughski-colorhug2-2.0.2.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                }
            ]
        },
        {
            "Name" : "GP106 [GeForce GTX 1060 6GB]",
            "DeviceId" : "71b677ca0f1bc2c5b804fa1d59e52064ce589293",
            "Guid" : [
                "b080a9ba-fff8-5de0-b641-26f782949f94",
                "f95bfce3-18e4-58b0-bd81-136457521383"
            ],
            "Plugin" : "optionrom",
            "Flags" : [
                "internal",
                "registered",
                "can-verify",
                "can-verify-image"
            ],
            "Vendor" : "NVIDIA Corporation",
            "VendorId" : "PCI:0x10DE",
            "Version" : "a1",
            "VersionFormat" : "plain",
            "Icons" : [
                "audio-card"
            ],
            "Created" : 1592899254
        },
        {
            "Name" : "Intel(R) Core™ i5-8400 CPU @ 2.80GHz",
            "DeviceId" : "4bde70ba4e39b28f9eab1628f9dd6e6244c03027",
            "Guid" : [
                "b9a2dd81-159e-5537-a7db-e7101d164d3f"
            ],
            "Plugin" : "cpu",
            "Flags" : [
                "internal",
                "registered"
            ],
            "Vendor" : "GenuineIntel",
            "Version" : "0xd6",
            "VersionFormat" : "hex",
            "Icons" : [
                "computer"
            ],
            "Created" : 1592899249
        },
        {
            "Name" : "SSDPR-CX400-256",
            "DeviceId" : "948241a24320627284597ec95079cc1341c90518",
            "Guid" : [
                "09fa3842-45bc-5226-a8ec-1668fc61f88f",
                "57d6b2ff-710d-5cd2-98be-4f6b8b7c5287",
                "36bebd37-b680-5d56-83a1-6693033d4098"
            ],
            "Summary" : "ATA Drive",
            "Plugin" : "ata",
            "Protocol" : "org.t13.ata",
            "Flags" : [
                "internal",
                "updatable",
                "require-ac",
                "registered",
                "needs-reboot",
                "usable-during-update"
            ],
            "Vendor" : "Phison",
            "VendorId" : "ATA:0x1987",
            "Version" : "SBFM61.3",
            "VersionFormat" : "plain",
            "Icons" : [
                "drive-harddisk"
            ],
            "Created" : 1592899254
        }
    ]
}
"""


GET_DEVICES_NO_VERSION = """{
    "Devices" : [
        {
            "Name" : "ColorHug2",
            "DeviceId" : "203f56e4e186d078ce76725e708400aafc253aac",
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
                "self-recovery",
                "add-counterpart-guids"
            ],
            "Vendor" : "Hughski Ltd.",
            "VendorId" : "USB:0x273F",
            "VersionFormat" : "triplet",
            "Icons" : [
                "colorimeter-colorhug"
            ],
            "InstallDuration" : 8,
            "Created" : 1592916092,
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
                    "Created" : 1482901200,
                    "Uri" : "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on the second half of batch 16</li><li>Fix the firmware upgrade process using new versions of fwupd</li></ul>",
                    "Filename" : "f038b5ca40e6d7c1c0299a9e1dcc129d5f6371b6",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "03c9c14db1894a00035ececcfae192865a710e52"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1450792062,
                    "Uri" : "https://fwupd.org/downloads/170f2c19f17b7819644d3fcc7617621cc3350a04-hughski-colorhug2-2.0.6.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on batch 16</li><li>Make the self test more sensitive to detect floating pins</li></ul>",
                    "Version" : "2.0.5",
                    "Filename" : "ae76c6b704b60f9d1d88dc2c8ec8a62d7b2331dc",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "4ee9dfa38df3b810f739d8a19d13da1b3175fb87"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1444059405,
                    "Uri" : "https://fwupd.org/downloads/f7dd4ab29fa610438571b8b62b26b0b0e57bb35b-hughski-colorhug2-2.0.5.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This unstable release adds the following features:</p><ul><li>Add TakeReadingArray to enable panel latency measurements</li><li>Speed up the auto-scaled measurements considerably, using 256ms as the smallest sample duration</li></ul>",
                    "Version" : "2.0.2",
                    "Filename" : "d4b3144daeb2418634f9d464d88d55590bcd9ac7",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "448527af3ce019d03dbb77aaebaa7eb893f1ea20"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 15680,
                    "Created" : 1416675439,
                    "Uri" : "https://fwupd.org/downloads/30a121f26c039745aeb5585252d4a9b5386d71cb-hughski-colorhug2-2.0.2.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                }
            ]
        },
        {
            "Name" : "ColorHug2",
            "DeviceId" : "203f56e4e186d078ce76725e708400aafc253aac",
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
                "self-recovery",
                "add-counterpart-guids"
            ],
            "Vendor" : "Hughski Ltd.",
            "Version" : "2.0.6",
            "VendorId" : "USB:0x273F",
            "VersionFormat" : "triplet",
            "Icons" : [
                "colorimeter-colorhug"
            ],
            "InstallDuration" : 8,
            "Created" : 1592916092,
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
                    "Created" : 1482901200,
                    "Uri" : "https://fwupd.org/downloads/0a29848de74d26348bc5a6e24fc9f03778eddf0e-hughski-colorhug2-2.0.7.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on the second half of batch 16</li><li>Fix the firmware upgrade process using new versions of fwupd</li></ul>",
                    "Version" : "2.0.6",
                    "Filename" : "f038b5ca40e6d7c1c0299a9e1dcc129d5f6371b6",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "03c9c14db1894a00035ececcfae192865a710e52"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1450792062,
                    "Uri" : "https://fwupd.org/downloads/170f2c19f17b7819644d3fcc7617621cc3350a04-hughski-colorhug2-2.0.6.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This stable release fixes the following problems:</p><ul><li>Fix the swapped LEDs on batch 16</li><li>Make the self test more sensitive to detect floating pins</li></ul>",
                    "Version" : "2.0.5",
                    "Filename" : "ae76c6b704b60f9d1d88dc2c8ec8a62d7b2331dc",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "4ee9dfa38df3b810f739d8a19d13da1b3175fb87"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 16384,
                    "Created" : 1444059405,
                    "Uri" : "https://fwupd.org/downloads/f7dd4ab29fa610438571b8b62b26b0b0e57bb35b-hughski-colorhug2-2.0.5.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                },
                {
                    "AppstreamId" : "com.hughski.ColorHug2.firmware",
                    "RemoteId" : "lvfs",
                    "Summary" : "Firmware for the Hughski ColorHug2 Colorimeter",
                    "Description" : "<p>This unstable release adds the following features:</p><ul><li>Add TakeReadingArray to enable panel latency measurements</li><li>Speed up the auto-scaled measurements considerably, using 256ms as the smallest sample duration</li></ul>",
                    "Version" : "2.0.2",
                    "Filename" : "d4b3144daeb2418634f9d464d88d55590bcd9ac7",
                    "Protocol" : "com.hughski.colorhug",
                    "Checksum" : [
                        "448527af3ce019d03dbb77aaebaa7eb893f1ea20"
                    ],
                    "License" : "GPL-2.0+",
                    "Size" : 15680,
                    "Created" : 1416675439,
                    "Uri" : "https://fwupd.org/downloads/30a121f26c039745aeb5585252d4a9b5386d71cb-hughski-colorhug2-2.0.2.cab",
                    "Homepage" : "http://www.hughski.com/",
                    "SourceUrl" : "https://github.com/hughski/colorhug2-firmware",
                    "Vendor" : "Hughski Limited",
                    "Flags" : [
                        "is-downgrade"
                    ],
                    "InstallDuration" : 8
                }
            ]
        },
        {
            "Name" : "GP106 [GeForce GTX 1060 6GB]",
            "DeviceId" : "71b677ca0f1bc2c5b804fa1d59e52064ce589293",
            "Guid" : [
                "b080a9ba-fff8-5de0-b641-26f782949f94",
                "f95bfce3-18e4-58b0-bd81-136457521383"
            ],
            "Plugin" : "optionrom",
            "Flags" : [
                "internal",
                "registered",
                "can-verify",
                "can-verify-image"
            ],
            "Vendor" : "NVIDIA Corporation",
            "VendorId" : "PCI:0x10DE",
            "VersionFormat" : "plain",
            "Icons" : [
                "audio-card"
            ],
            "Created" : 1592899254
        },
        {
            "Name" : "Intel(R) Core™ i5-8400 CPU @ 2.80GHz",
            "DeviceId" : "4bde70ba4e39b28f9eab1628f9dd6e6244c03027",
            "Guid" : [
                "b9a2dd81-159e-5537-a7db-e7101d164d3f"
            ],
            "Plugin" : "cpu",
            "Flags" : [
                "internal",
                "registered"
            ],
            "Vendor" : "GenuineIntel",
            "Version" : "0xd6",
            "VersionFormat" : "hex",
            "Icons" : [
                "computer"
            ],
            "Created" : 1592899249
        },
        {
            "Name" : "SSDPR-CX400-256",
            "DeviceId" : "948241a24320627284597ec95079cc1341c90518",
            "Guid" : [
                "09fa3842-45bc-5226-a8ec-1668fc61f88f",
                "57d6b2ff-710d-5cd2-98be-4f6b8b7c5287",
                "36bebd37-b680-5d56-83a1-6693033d4098"
            ],
            "Summary" : "ATA Drive",
            "Plugin" : "ata",
            "Protocol" : "org.t13.ata",
            "Flags" : [
                "internal",
                "updatable",
                "require-ac",
                "registered",
                "needs-reboot",
                "usable-during-update"
            ],
            "Vendor" : "Phison",
            "VendorId" : "ATA:0x1987",
            "Version" : "SBFM61.3",
            "VersionFormat" : "plain",
            "Icons" : [
                "drive-harddisk"
            ],
            "Created" : 1592899254
        }
    ]
}
"""

HEADS_XML = """<?xml version='1.0' encoding='utf-8'?>
<components origin="lvfs" version="0.9">
  <component type="firmware">
    <id>com.3mdeb.heads.x230.firmware</id>
    <name>Heads Lenovo x230 System Update</name>
    <summary>Lenovo x230 heads system firmware</summary>
    <description>
      <p>Lenovo x230 heads system firmware</p>
    </description>
    <provides>
      <firmware type="flashed">596c3466-0506-5ca5-a68f-dc34532a93d3</firmware>
    </provides>
    <url type="homepage">http://osresearch.net/</url>
    <metadata_license>CC0-1.0</metadata_license>
    <project_license>GPLv2</project_license>
    <developer_name>coreboot</developer_name>
    <X-categories>
      <category>X-System</category>
    </X-categories>
    <releases>
      <release version="4.19.0" timestamp="1598918400" urgency="high">
        <location>https://fwupd.org/downloads/10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab</location>
        <checksum type="sha1" filename="10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab" target="container">cf3af2382cbd3c438281d33daef63b69af7854cd</checksum>
        <checksum type="sha256" filename="10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab" target="container">6de5d65e0b911f05ae3d5bb18ad5547cb5bb10c88066686d79e369c6c67cdd11</checksum>
        <checksum type="sha1" filename="firmware.rom" target="content">fe15f41dc8822a89b8e24713f96d015d2877482e</checksum>
        <checksum type="sha256" filename="firmware.rom" target="content">cb78a05ce09b4ea67ce576d696ac00cb1bb4d5d589da8f41cfb2dae75d579023</checksum>
        <description>
          <p>Lenovo x230 heads system firmware</p>
        </description>
        <url type="details">https://fwupd.org/downloads/10176eb94fa364e5a3ce1085d8076f38a5cdc92865a98f8bd2cf711e5c645072-heads_coreboot_x230-v4_19_0.cab</url>
        <url type="source">https://github.com/osresearch/heads</url>
        <size type="installed">12582912</size>
        <size type="download">12591924</size>
      </release>
    </releases>
  </component>
  <component type="firmware">
    <id>com.Libretrend.LT1000.firmware</id>
    <name>LT1000 Coreboot Device Update</name>
    <summary>Firmware for the Libretrend LT1000 platform</summary>
    <description>
      <p>The platform can be updated using flashrom (internal programmer).</p>
    </description>
    <provides>
      <firmware type="flashed">52b68c34-6b31-5ecc-8a5c-de37e666ccd5</firmware>
    </provides>
    <url type="homepage">http://www.3mdeb.com/</url>
    <metadata_license>CC0-1.0</metadata_license>
    <project_license>Proprietary</project_license>
    <developer_name>Libretrend</developer_name>
    <X-categories>
      <category>X-Device</category>
    </X-categories>
    <custom>
      <value key="LVFS::VersionFormat">quad</value>
      <value key="LVFS::UpdateProtocol">org.flashrom</value>
    </custom>
    <releases>
      <release version="4.9.0.1" timestamp="1548460800" urgency="high">
        <location>https://fwupd.org/downloads/83d2fb2e3e8340fa9ceadd2fde38d2cdb2b731e3-com.Libretrend.LT1000.firmware.cab</location>
        <checksum type="sha1" filename="83d2fb2e3e8340fa9ceadd2fde38d2cdb2b731e3-com.Libretrend.LT1000.firmware.cab" target="container">be118fc3e970698d67d8dc9dbd11147529eeb13d</checksum>
        <checksum type="sha256" filename="83d2fb2e3e8340fa9ceadd2fde38d2cdb2b731e3-com.Libretrend.LT1000.firmware.cab" target="container">e928e47fe6c0f161efc6b5020be628b9f90f65cf65f4b2c7a12cf55a59d885be</checksum>
        <checksum type="sha1" filename="com.Libretrend.LT1000.firmware.bin" target="content">96bffbef9c593352a6717e21caccee60b309a162</checksum>
        <checksum type="sha256" filename="com.Libretrend.LT1000.firmware.bin" target="content">8817749a65766cc5543a74f3c2d8ffdd3338664fddc36bd5d40965cf20ce4b68</checksum>
        <description>
          <p>This release features:</p>
          <ul>
            <li>Moved console initialization and sign-of-life to bootblock</li>
            <li>Fixed the CBFS size to 6MB</li>
            <li>Minor build fixes</li>
            <li>Rebased on official coreboot repository commit 2ef569a4</li>
          </ul>
        </description>
        <size type="installed">8388608</size>
        <size type="download">1167446</size>
      </release>
      <release version="4.8.0.4" timestamp="1544400000" urgency="high">
        <location>https://fwupd.org/downloads/77c84dc75f74b225eaa7508b1f278fd9f5177bfc-com.Libretrend.LT1000.firmware.cab</location>
        <checksum type="sha1" filename="77c84dc75f74b225eaa7508b1f278fd9f5177bfc-com.Libretrend.LT1000.firmware.cab" target="container">f8e7b545c2224da0f74d6e6ca75682202b95b541</checksum>
        <checksum type="sha256" filename="77c84dc75f74b225eaa7508b1f278fd9f5177bfc-com.Libretrend.LT1000.firmware.cab" target="container">39dcf80a930823fd01c9209132e50b1e8ac9755eeeb8b5946194537345255e3f</checksum>
        <checksum type="sha1" filename="com.Libretrend.LT1000.firmware.bin" target="content">2dc5614fb76124a42f6c86fc4628b25359de1198</checksum>
        <checksum type="sha256" filename="com.Libretrend.LT1000.firmware.bin" target="content">2cca5704aeee2f6f6f094fcc911643ab32f72948d914596bca6dc0b8a94c9712</checksum>
        <description>
          <p>This release features:</p>
          <ul>
            <li>Support for Libretrend TPM2.0 module</li>
            <li>Added bootorder with internal SSD as first priority</li>
            <li>The LED near power button will shine red on any hard disk activity</li>
            <li>SeaBIOS updated to rel-1.12.0</li>
            <li>Synced and rebased to official coreboot commit 967b1963</li>
          </ul>
        </description>
        <size type="installed">8388608</size>
        <size type="download">1852546</size>
      </release>
      <release version="4.8.0.3" timestamp="1537833600" urgency="high">
        <location>https://fwupd.org/downloads/47f19f4cde49ac06febf37e0b0b64f66a81a9c07-com.Libretrend.LT1000.firmware.cab</location>
        <checksum type="sha1" filename="47f19f4cde49ac06febf37e0b0b64f66a81a9c07-com.Libretrend.LT1000.firmware.cab" target="container">7d13a74c288341e2f099e61815beb58e96c9e055</checksum>
        <checksum type="sha256" filename="47f19f4cde49ac06febf37e0b0b64f66a81a9c07-com.Libretrend.LT1000.firmware.cab" target="container">7bf9c9188f116a00123a1df6a63e5aaa867da4a9018da7452734a894310b7b9a</checksum>
        <checksum type="sha1" filename="com.Libretrend.LT1000.firmware.bin" target="content">d2d49b0c187449a1660ac3afb5bcfc35cdfc873b</checksum>
        <checksum type="sha256" filename="com.Libretrend.LT1000.firmware.bin" target="content">4c6ab6351d0614dd41b5ae108d474573bdd26562acf9f6633dcc696b45bfdf30</checksum>
        <description>
          <p>This release features:</p>
          <ul>
            <li>DIMMs presence is determined automatically</li>
            <li>Enabled all SATA ports on the board</li>
            <li>Configured PC speaker GPIO</li>
          </ul>
        </description>
        <size type="installed">8388608</size>
        <size type="download">1167977</size>
      </release>
      <release version="4.8.0.2" timestamp="1535846400" urgency="high">
        <location>https://fwupd.org/downloads/87c3110d6e1fd2be9c860f1b45b6291ffae0b6a6-com.Libretrend.LT1000.firmware.cab</location>
        <checksum type="sha1" filename="87c3110d6e1fd2be9c860f1b45b6291ffae0b6a6-com.Libretrend.LT1000.firmware.cab" target="container">01c6d751a5b58c78ae2f93b4442059e5390d4377</checksum>
        <checksum type="sha256" filename="87c3110d6e1fd2be9c860f1b45b6291ffae0b6a6-com.Libretrend.LT1000.firmware.cab" target="container">96ebf025fbb7b5d9320a76500724f104b2b29baf276b6abc316dd0c35116b60c</checksum>
        <checksum type="sha1" filename="com.Libretrend.LT1000.firmware.bin" target="content">1b68ef2b4285bcc494d717e447ce93b5dca0c800</checksum>
        <checksum type="sha256" filename="com.Libretrend.LT1000.firmware.bin" target="content">9182f4c2530d0b1a77fcbf1efdcae45013c34127f2c8fa730930f251fe93fff9</checksum>
        <description>
          <p>This release adds integration with new Intel FSP.</p>
        </description>
        <size type="installed">8388608</size>
        <size type="download">1166270</size>
      </release>
    </releases>
    <requires>
      <id compare="ge" version="1.1.2">org.freedesktop.fwupd</id>
      <id compare="ge" version="1.1.2">org.freedesktop.fwupd</id>
      <id compare="ge" version="1.1.2">org.freedesktop.fwupd</id>
      <id compare="ge" version="1.1.2">org.freedesktop.fwupd</id>
    </requires>
  </component>
</components>
"""
