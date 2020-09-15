# Heads update

The Heads update was tested on the `Lenovo ThinkPad x230`.

## Requirements

You need to build and flash Heads ROM from the
[3mdeb fork](https://github.com/3mdeb/heads/tree/qubes-fwupd).
Currently, you need to pass custom metadata URL:

```
https://fwupd.org/downloads/firmware-3c81bfdc9db5c8a42c09d38091944bc1a05b27b0.xml.gz
```

You will find there Heads ROMs for ThinkPad x230.

## Update process

ThinkPad x230 is now the only laptop that has Heads ROM in the custom LVFS
storage. Nevertheless, qubes-fwupd has already implemented a `device` flag, that
will allow updates for other hardware.

At first run the qubes-fwupd Heads update.

```
sudo qubes-fwupdmgr update-heads --device=x230 --url=https://fwupd.org/downloads/firmware-3c81bfdc9db5c8a42c09d38091944bc1a05b27b0.xml.gz
```

Press Y to reboot the device.

[![asciicast](https://asciinema.org/a/RVXLOe2CkHtkYqjJumsy0Hw5d.svg)](https://asciinema.org/a/RVXLOe2CkHtkYqjJumsy0Hw5d)

In the main menu, choose `options` and then go to `Flash/Update the BIOS`

![img](img/heads_options.jpg)

Decide to retain or erase the settings.

![img](img/heads_firmware_managment_menu.jpg)

The tool will inform you that heads update has been detected in `/boot`
directory. If you will decide not to update, you will be asked to attach the
USB drive.

![img](img/heads_detected.jpg)

Select a ROM file.

![img](img/heads_selecting_rom.jpg)

Press yes to confirm the choice. The Heads update will begin.


![img](img/heads_flash_rom.jpg)

Wait until the end of the update process.

![img](img/heads_update_process.jpg)

Press OK to reboot the system.

![img](img/heads_success.jpg)

## Test

Change directory to `/usr/share/qubes-fwupd` and run test case with sudo
privileges.

### Qubes OS R4.0

```
# python3.6 -m unittest -v test.test_qubes_fwupd_heads
```

[![asciicast](https://asciinema.org/a/oZnmBN6hUcXBebb1buzBeT6oT.svg)](https://asciinema.org/a/oZnmBN6hUcXBebb1buzBeT6oT)


### Qubes OS R4.1

qubes-fwupd supports Heads updates in this OS version but currently, the Qubes
4.1 does not work correctly under the Heads. You can find more information in
the following [GitHub issue](https://github.com/osresearch/heads/issues/789).

```
# python3 -m unittest -v test.test_qubes_fwupd_heads
```
