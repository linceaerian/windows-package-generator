# Windows Package Generator

This project can be use to create msi package for windows from your own app sources 


## Summary

* [Dependencies](#dependencies)
* [Installation](#installation)
* [Developers Documentation](#developers-documentation)
* [Users Documentation](#users-documentation)

## Dependencies

- Python 3 :
  - pyCLI
  - xmltodict
- Linux :
  - wixl
  - python3
  - pip3

## Installation

Clone this repo on your computer, go inside the local repo and install it with :
```bash
sudo pip3 install .
```

## Developers Documentation

Not yet

## Users Documentation


```bash
usage: windows_package_generator [-h] [-a ARCH] [-o OUTPUT] [-m MANUFACTURER]
                                 [-n NAME] [-e EXECUTABLE]
                                 [--description DESCRIPTION] [-u UPGRADE_CODE]
                                 [-v VERSION] [-i ICON] [-d INSTALL_DIR] [-r]
                                 [-l]
                                 Sources

positional arguments:
  Sources               Your sources directory path

optional arguments:
  -h, --help            show this help message and exit
  -a ARCH, --arch ARCH  Architecture of the output package (x86 or x64)
  -o OUTPUT, --output OUTPUT
                        Output file (default : /tmp/output.msi
  -m MANUFACTURER, --manufacturer MANUFACTURER
                        Name of the manufacturer
  -n NAME, --name NAME  Name of the app
  -e EXECUTABLE, --executable EXECUTABLE
                        Specify file to create shortcuts for
  --description DESCRIPTION
                        (Optional) Description
  -u UPGRADE_CODE, --upgrade-code UPGRADE_CODE
                        The upgrade code (Auto-generate from file name if not
                        specified
  -v VERSION, --version VERSION
                        Version number
  -i ICON, --icon ICON  The icon.ico path
  -d INSTALL_DIR, --install-dir INSTALL_DIR
                        The installation directory name
  -r, --root-install    Install program in C:/
  -l, --local           Local user install (in AppData)
```
