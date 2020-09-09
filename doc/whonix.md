# Whonix support

The qubes-fwupd uses the sys-whonix VM as the update VM to handle downloading
updates and metadata via Tor. The tests detect if sys-whonix is running, but
do not check if you are connected with Tor. So before running the test make sure
that sys-whonix has access to the network.

## Refresh

```
$ sudo qubes-fwupdmgr refresh --whonix
```

[![asciicast](https://asciinema.org/a/5zJhIZeATwx9OYVOELoK69ZMo.svg)](https://asciinema.org/a/5zJhIZeATwx9OYVOELoK69ZMo)

## Update

```
$ sudo qubes-fwupdmgr update --whonix
```

[![asciicast](https://asciinema.org/a/fsqv5Q3Bzi79LoCqoQB2RKts0.svg)](https://asciinema.org/a/fsqv5Q3Bzi79LoCqoQB2RKts0)

## Downgrade

```
$ sudo qubes-fwupdmgr downgrade --whonix
```

[![asciicast](https://asciinema.org/a/KyhQf9vQ35j8H5A7lP9JJd0oB.svg)](https://asciinema.org/a/KyhQf9vQ35j8H5A7lP9JJd0oB)
