RPM_SPEC_FILES.dom0 := rpm_spec/qubes-fwupd-dom0.spec
RPM_SPEC_FILES.vm := rpm_spec/qubes-fwupd-vm.spec

RPM_SPEC_FILES := $(RPM_SPEC_FILES.$(PACKAGE_SET))
