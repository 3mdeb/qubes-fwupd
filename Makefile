NAME := qubes-fwupd

ifndef NAME
$(error "You can not run this Makefile without having NAME defined")
endif
ifndef VERSION
VERSION := $(shell cat version)
endif

FWUPD_QUBES_DIR := /usr/share/qubes-fwupd

install-dom0:
	install -m 755 -D src/qubes_fwupdmgr.py $(DESTDIR)$(FWUPD_QUBES_DIR)/src/qubes_fwupdmgr.py
	install -m 755 -D src/fwupd_receive_updates.py $(DESTDIR)$(FWUPD_QUBES_DIR)/src/fwupd_receive_updates.py
	install -m 755 -D src/fwupd-dom0-update $(DESTDIR)$(FWUPD_QUBES_DIR)/src/fwupd-dom0-update
	install -m 644 -D src/__init__.py $(DESTDIR)$(FWUPD_QUBES_DIR)/src/__init__.py
	install -m 755 -D test/fwupd_logs.py $(DESTDIR)$(FWUPD_QUBES_DIR)/test/fwupd_logs.py
	install -m 755 -D test/test_qubes_fwupdmgr.py $(DESTDIR)$(FWUPD_QUBES_DIR)/test/test_qubes_fwupdmgr.py
	install -m 644 -D test/__init__.py $(DESTDIR)$(FWUPD_QUBES_DIR)/test/__init__.py
	install -m 644 -D test/logs/get_devices.log $(DESTDIR)$(FWUPD_QUBES_DIR)/test/logs/get_devices.log
	install -m 644 -D test/logs/get_updates.log $(DESTDIR)$(FWUPD_QUBES_DIR)/test/logs/get_updates.log
	install -m 644 -D test/logs/help.log $(DESTDIR)$(FWUPD_QUBES_DIR)/test/logs/help.log
	install -m 644 -D test/logs/firmware.metainfo.xml $(DESTDIR)$(FWUPD_QUBES_DIR)/test/logs/firmware.metainfo.xml
	install -m 644 -D test/logs/metainfo_name/firmware.metainfo.xml $(DESTDIR)$(FWUPD_QUBES_DIR)/test/logs/metainfo_name/firmware.metainfo.xml
	install -m 644 -D test/logs/metainfo_version/firmware.metainfo.xml $(DESTDIR)$(FWUPD_QUBES_DIR)/test/logs/metainfo_version/firmware.metainfo.xml

install-vm:
	install -m 755 -D src/updatevm/fwupd-download-updates.sh $(DESTDIR)$(FWUPD_QUBES_DIR)/fwupd-download-updates.sh
	install -m 755 -D src/usbvm/fwupd_usbvm_validate.py $(DESTDIR)$(FWUPD_QUBES_DIR)/fwupd_usbvm_validate.py

install-whonix:
	install -m 755 -D src/updatevm/fwupd-download-updates.sh $(DESTDIR)$(FWUPD_QUBES_DIR)/fwupd-download-updates.sh
	install -d /home/user/.cache/fwupd

clean:
	rm -rf pkgs
