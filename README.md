# qubes-fwupd

fwupd wrapper for QubesOS [R4.1](https://openqa.qubes-os.org/tests/9430#downloads)

WARNING: The repository is currently under development. Use it at your own risk.

## Usage

```
qubes-fwupd [OPTION…]:
    get-devices:        Get all devices that support firmware updates
    get-updates:        Gets the list of updates for connected hardware
    refresh:            Refresh metadata from lvfs server
    update:             Updates chosen device to latest firmware version
    downgrade:          Downgrade chosen device to chosen firmware version
    clean:              Deletes all cached update files
Help:
    -h --help:          Show the help
```

## Installation

For development purpose:

1. Clone [qubes-builder](https://github.com/QubesOS/qubes-builder)

```bash
git clone https://github.com/QubesOS/qubes-builder.git
cd qubes-builder
```

2. Use your desired `builder.conf` file from `example-configs` directory.

3. Edit the `builder.conf` by adding:

```
GIT_URL_fwupd = https://github.com/3mdeb/qubes-fwupd
NO_CHECK += fuwpd
...

COMPONENTS = ...
        builder-debian \
        builder-rpm \
        fwupd
```

4. Download sources used to build Qubes:

```
make get-sources
```

5. Install dependencies:

```
make install-deps
```

6. You may need remount command before building package:

```
make remount
```

6. Build RPM package:

```
make fwupd
```

7. The result will be placed as RPM package in:
  -- dom0 package - `qubes-builder/qubes-src/fwupd/pkgs/dom0-fc32/x86_64`
  -- vm package - `qubes-builder/qubes-src/fwupd/pkgs/dom0-fc32/x86_64`

8. Run fedora templateVM and copy RPM from qubes-builder VM to fedoraVM:

```
qvm-copy qubes-fwupd-vm-0.1.3-1.fc32.x86_64.rpm
```

9. Install install dependencies

```
# dnf install cabextract fwudp
```

10. Go to `~/QubesIncoming/fwupd` and compare a checksum of the package in
TemplateVM and qubes-builder VM. If checksums match install the package:

```
# rpm -i qubes-fwupd-vm-0.1.3-1.fc32.x86_64.rpm
```

11. Shutdown TemplateVM

12. Run terminal in the dom0 and copy package:

```
qvm-run --pass-io <qubes-builder-vm-name> \
'cat <qubes-builder-repo-path>/qubes-src/fwupd/pkgs/dom0-fc32/x86_64/qvm-copy qubes-fwupd-vm-0.1.3-1.fc32.x86_64.rpm' > \
qvm-copy qubes-fwupd-vm-0.1.3-1.fc32.x86_64.rpm
```

13. Compare a checksum of the package in dom0 and qubes-builder VM.
If checksums match install the package:

```
# rpm -i qubes-fwupd-dom0-0.1.3-1.fc32.x86_64.rpm
```

14. Run the tests to verify that the installation process has been successful

## Testing

### Outside the Qubes OS

Tests could be run outside the Qubes OS. If test requirement is not meet, the
test is ommited. Run the tests in the repo directory:

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

In the dom0 move to:

```
cd /usr/share/qubes-fwupd/
```

Run the tests with sudo privileges:

```
# python3 -m unittest -v test.test_qubes_fwupdmgr
```

[![asciicast](https://asciinema.org/a/TgHOkLnD2YICxB0U80PVcQGqX.svg)](https://asciinema.org/a/TgHOkLnD2YICxB0U80PVcQGqX)
