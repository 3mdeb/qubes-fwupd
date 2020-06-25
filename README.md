# qubes-fwupd

fwupd wrappers for QubesOS

WARNING: The repository is currently under development. Use it at your own risk.

## Installation

For development proposes:

1. Run a personal VM in Qubes OS

2. Run a terminal in the personal VM and clone the repository:

```
git clone git@github.com:3mdeb/qubes-fwupd.git
```

3. Zip the repository and check the sha256 sum

4. Run a terminal in dom0 and copy the zip file

```
qvm-run --pass-io personal 'cat ~/Project/fwupd-implementation/qubes-fwupd.zip' > qubes-fwupd.zip
```

5. Inspect the checksum and unzip the repository

6. Run the setup script:

```
sudo ./setup
```

7. Run the tests to verify that the installation process has been successful

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

## Testing

You don't need Qubes OS to run the tests during development. In the top
repo directory run the tests:

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

To verify instalation in dom0 move to:

```
cd /usr/share/fwupd-qubes/
```

Then run the tests with sudo privileges:

```
# python3 -m unittest -v test.test_qubes_fwupdmgr
```
