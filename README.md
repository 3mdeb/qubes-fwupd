# qubes-fwupd

[![Build Status](https://travis-ci.com/3mdeb/qubes-fwupd.svg?branch=master)](https://travis-ci.com/3mdeb/qubes-fwupd)

fwupd wrapper for QubesOS

## Table of Contents

* [Requirements](#Requirements)
* [Usage](#Usage)
* [Installation](#Installation)
* [Testing](#Testing)
* [Whonix support](doc/whonix.md)
* [UEFI capsule update](doc/uefi_capsule_update.md)
* [Heads update](doc/heads_update.md)

## OS Requirements

**Operating System:** Qubes OS R4.1 or Qubes OS R4.0

**Admin VM (dom0):** Fedora 25 or higher

**Template VM:** Fedora 30

**Whonix VM:** whonix-gw-15

**fwupd version - dom0:** 0.9.5 or higher

**fwupd version - VMs:** 1.2.6 or higher

qubes-fwupd do not support dom0 updates and downgrades for fwupd 0.9.5 and
older. Use sys-usb to update external devices.

## Usage

```
==========================================================================================
Usage:
==========================================================================================
        Command:                        qubes-fwupdmgr [OPTION…][FLAG..]
        Example:                        qubes-fwupdmgr refresh --whonix --url=<url>

Options:
==========================================================================================
        get-devices:                    Get all devices that support firmware updates
        get-updates:                    Get the list of updates for connected hardware
        refresh:                        Refresh metadata from remote server
        update:                         Update chosen device to latest firmware version
        update-heads:                   Updates heads firmware to the latest version
        downgrade:                      Downgrade chosen device to chosen firmware version
        clean:                          Delete all cached update files

Flags:
==========================================================================================
        --whonix:                       Download firmware updates via Tor
        --device:                       Specify device for heads update (default - x230)
        --url:                          Address of the custom metadata remote server

Help:
==========================================================================================
        -h --help:                      Show help options
```

## Installation

For development purpose:

1. Clone [qubes-builder](https://github.com/QubesOS/qubes-builder).
  Make sure that you have enough space in your VM. You will need at least 10GB.

```bash
$ git clone https://github.com/QubesOS/qubes-builder.git
$ cd qubes-builder
```

2. Copy specific config file from the `example-configs` directory

```
cp example-configs/qubes-os-master.conf builder.conf
```

3. Add the following to the `builder.conf`

```
GIT_URL_fwupd = https://github.com/3mdeb/qubes-fwupd
NO_CHECK += fuwpd
...

COMPONENTS = ...
        builder \
        builder-debian \
        builder-rpm \
        fwupd
```

4. Download sources

```
$ make get-sources
```

5. Install dependencies

```
$ make install-deps
```

6. Install python2

```
# dnf install python2
```

7. You may need to remount the current filesystem

```
$ make remount
```

8. Build packages (First build takes close to 30 min,
  so you can grab some coffee)

```
$ make fwupd
```

9. The build artifacts are placed in:
  -- dom0 package - `qubes-builder/qubes-src/fwupd/pkgs/dom0-fc32/x86_64`
  -- vm package - `qubes-builder/qubes-src/fwupd/pkgs/vm-fc32/x86_64`
  -- whonix package - `qubes-builder/qubes-src/fwupd/pkgs/vm-buster`

10. Run fedora template VM and copy VM package from qubes builder:

```
$ qvm-copy qubes-fwupd-vm-0.2.0-1.fc32.x86_64.rpm
```

11. Install package dependencies

```
# dnf install cabextract fwudp
```

12. Run terminal in the template VM and go to
`~/QubesIncoming/<qubes-builderVM>`. Compare sha sums of the package in
TemplateVM and qubes-builder VM. If they match, install the package:

```
# rpm -U qubes-fwupd-vm-0.2.0-1.fc32.x86_64.rpm
```

13. Shutdown TemplateVM

14. Run whonix-gw-15 and copy whonix a package from qubes builder VM

```
$ qvm-copy qubes-fwupd-vm-whonix_0.2.0+deb10u1_amd64.deb
```

15. Download dependencies

```
# apt install cabextract fwudp
```

16. Run terminal in the whonix-gw-15 and go to `~/QubesIncoming/qubes-builder`.
Compare sha sums of the package in TemplateVM and qubes-builder VM. If they
match, install the package:

```
# dpkg -i qubes-fwupd-vm-whonix_0.2.0+deb10u1_amd64.deb
```

17. Shutdown whonix-gw-15

18. Run dom0 terminal in the dom0 and copy package

```
$ qvm-run --pass-io <qubes-builder-vm-name> \
'cat <qubes-builder-repo-path>/qubes-src/fwupd/pkgs/dom0-fc32/x86_64/qubes-fwupd-dom0-0.2.0-1.fc32.x86_64.rpm' > \
qubes-fwupd-vm-0.2.0-1.fc32.x86_64.rpm
```

19. Install package dependencies

```
# qubes-dom0-update cabextract fwudp python36
```

20. Make sure that sys-firewall, sys-whonix, and sys-usb (if exists) are running.

21. Compare the sha sums of the package in dom0 and qubes-builder VM.
If they match, install the package:

```
# rpm -U qubes-fwupd-dom0-0.2.0-1.fc32.x86_64.rpm
```

22. Reboot system (or reboot sys-firewall, sys-whonix, and sys-usb)

23. Run the tests to verify the installation process

## Testing

### Outside the Qubes OS

A test case covers the whole qubes_fwupdmgr script. It could be run outside the
Qubes OS. If the requirements of a single test are not met, it will be omitted.
To run the tests, move to the repo directory and type the following:

```
$ python3 -m unittest -v test.test_qubes_fwupdmgr

test_clean_cache (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_downgrade_firmware (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'Required device not connected'
test_download_firmware_updates (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_download_metadata (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_get_devices (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_get_devices_qubes (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_get_updates (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_get_updates_qubes (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_help (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_output_crawler (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_parse_downgrades (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_parse_parameters (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_parse_updates_info (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_refresh_metadata (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... skipped 'requires Qubes OS'
test_user_input_choice (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_user_input_downgrade (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_user_input_empty_list (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_user_input_n (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_verify_dmi (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_verify_dmi_argument_version (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_verify_dmi_version (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok
test_verify_dmi_wrong_vendor (test.test_qubes_fwupdmgr.TestQubesFwupdmgr) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.003s

OK (skipped=8)
```

### In the Qubes OS

In the dom0, move to:

```
$ cd /usr/share/qubes-fwupd/
```

#### Qubes OS 4.1

Run the tests with sudo privileges:

```
# python3 -m unittest -v test.test_qubes_fwupdmgr
```

Note: If the whonix tests failed, make sure that you are connected to the Tor

[![asciicast](https://asciinema.org/a/TgHOkLnD2YICxB0U80PVcQGqX.svg)](https://asciinema.org/a/TgHOkLnD2YICxB0U80PVcQGqX)


#### Qubes OS 4.0

Make sure that you are using python 3.6!!!

```
# python36 -m unittest -v test.test_qubes_fwupdmgr
```

Note: If the whonix tests failed, make sure that you are connected to the Tor

[![asciicast](https://asciinema.org/a/HRf27PXEHnLsiQtlwhb55l9Ni.svg)](https://asciinema.org/a/HRf27PXEHnLsiQtlwhb55l9Ni)

## Whonix support

```
# qubes-fwupdmgr [refresh/update/downgrade] --whonix [FLAG]
```

More specified information you will find in the
[whonix documentation](doc/whonix.md).

## UEFI capsule update

```
# qubes-fwupdmgr [update/downgrade]
```

Requirements and more specified information you will find in the
[UEFI capsule update documentation](doc/uefi_capsule_update.md).


## Heads update

```
# qubes-fwupdmgr update-heads --device=x230 --url=<custom-metadata-url>
```

Requirements and more specified information you will find in the
[heads update documentation](doc/heads_udpate.md).

