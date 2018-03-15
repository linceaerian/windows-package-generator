#!/usr/bin/env python3
import html
import random
import shlex
import uuid
from urllib.parse import quote

import cli.app
import subprocess
import os
import xmltodict


def generate_xml(options):
    """
    Generate the whole xml file needed by wixl and store it in /tmp
    :param options: options passed by cli
    :return: xml file name
    """
    files, dirs, ids = get_components(options["Sources"], options)
    output = {
        "Wix": {
            "@xmlns": "http://schemas.microsoft.com/wix/2006/wi",
            "Product": {
                "@Id": "*",
                "@Name": options["name"],
                "@UpgradeCode": options["upgrade_code"],
                "@Language": "1033",
                "@Codepage": "1252",
                "@Version": options["version"],
                "@Manufacturer": options["manufacturer"],
                "Property": [
                    {
                        "@Id": "PREVIOUSVERSIONSINSTALLED",
                        "@Secure": "yes"
                    },
                    {
                        "@Id": "ARPPRODUCTION",
                        "@Value": "icon.ico"
                    }
                ],
                "Upgrade": {
                    "@Id": options["upgrade_code"],
                    "UpgradeVersion": {
                        "@Minimum": "0.0.0",
                        "@Property": "PREVIOUSVERSIONINSTALLED",
                        "@IncludeMaximum": "yes",
                        "@IncludeMinimum": "yes",
                    }
                },
                "InstallExecuteSequence": {
                    "RemoveExistingProducts": {
                        "@Before": "InstallInitilize"
                    }
                },
                "Package": {
                    "@InstallerVersion": "200",
                    "@Compressed": "yes",
                    "@Comments": "Windows Installer Package",
                    "@InstallScope": "perUser" if options["local"] else "perMachine"
                },
                "Media": {
                    "@Id": "1",
                    "@Cabinet": "app.cab",
                    "@EmbedCab": "yes"
                },
                "Icon": {
                    "@Id": "icon.ico",
                    "@SourceFile": options["icon"],
                },
                "Directory": {
                    "@Id": "TARGETDIR",
                    "@Name": "SourceDir",
                    "Directory": {
                        "@Id": get_programs_folder(options),
                        "Directory": {
                            "@Id": "INSTALLDIR",
                            "@Name": options["install_dir"],
                            "Component": files,
                            "Directory": dirs,
                        },
                    },
                },
                "Feature": {
                    "@Id": "App",
                    "@Level": "1",
                    "ComponentRef": ids
                },
            },
        }
    }

    if options["root_install"]:
        output["Wix"]["Product"]["Directory"]["Directory"] = {
            "@Id": "INSTALLDIR",
            "@Name": options["install_dir"],
            "Component": files,
            "Directory": dirs,
        }

    xml_string = xmltodict.unparse(output, pretty=True)

    filename = str(random.getrandbits(256)) + ".xml"

    with open("/tmp/" + filename, mode="w") as f:
        f.writelines(xml_string)

    return filename


def file_el(path, root, name):
    """
    Create a file object
    :param path: path of the file
    :param root: path of the file in sources
    :param name: name of the file
    :return: file object
    """
    id = html.escape(os.path.join(path, name))
    return {"File": {
        "@Id": quote(id.replace(root, "").strip("/")).replace("/", "%2F"),
        "@Source": os.path.join(root, id),
        "@Name": name
    },
        "@Id": quote(id.replace(root, "").strip("/")).replace("/", "%2F"),
        "@Guid": "*"
    }


def add_shortcut(file, options):
    """
    Add shortcuts to file xml object
    :param file: A file object in json
    :param options: options passed in cli
    :return: file object with shortcuts added
    """
    shortcuts = [
        {
            "@Id": "StartMenuShortcut",
            "@Advertise": "yes",
            "@Icon": "icon.ico",
            "@Name": options["name"],
            "@Directory": "ProgramMenuFolder",
            "@WorkingDirectory": "INSTALLDIR",
            "@Description": options["description"] or options["manufacturer"]
        },
        {
            "@Id": "DesktopShortcut",
            "@Advertise": "yes",
            "@Icon": "icon.ico",
            "@Name": options["name"],
            "@Directory": "DesktopFolder",
            "@WorkingDirectory": "INSTALLDIR",
            "@Description": options["description"] or options["manufacturer"]
        }
    ]
    file["Shortcut"] = shortcuts

    return file


def get_components(path, options):
    """
    Get project files in path recursively
    :param path: String path where search
    :param options: options passed by cli
    :return: files, dirs, id: file array, dirs array and ids array
    """
    ids = []
    files = []
    dirs = []

    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            # is file
            file = file_el(path, options["Sources"], f)
            if options["executable"]:
                if options["executable"] in os.path.join(path, f):
                    print(os.path.join(path, f))
                    file = add_shortcut(file, options)

            files.append(file)
            ids.append({"@Id": file["File"]["@Id"]})

            pass
        elif os.path.isdir(os.path.join(path, f)):
            # is dir
            id = os.path.join(path.replace(options["Sources"], ""), f).strip("/")
            a, b, c = get_components(os.path.join(path, f), options)
            directory = {
                "@Id": quote(id).replace("/", "%2F"),
                "@Name": f,
                "Component": a,
                "Directory": b
            }

            dirs.append(directory)
            for id_val in c:
                ids.append(id_val)
            pass

    return files, dirs, ids


def get_programs_folder(options):
    if options["local"]:
        return "LocalAppDataFolder"
    else:
        if options["arch"] is "x64":
            return "ProgramFiles64Folder"
        else:
            return "ProgramFilesFolder"


@cli.app.CommandLineApp
def windows_package_generator(app):
    options = vars(app.params)
    if not options["upgrade_code"]:
        options["upgrade_code"] = uuid.uuid3(uuid.NAMESPACE_DNS, options["name"])

    print("Start generation")
    xml_file = generate_xml(options)

    print("Calling wixl")
    subprocess.call(shlex.split("wixl " + " /tmp/" + xml_file + " -a " + options["arch"] + " -o " + options["output"]))
    subprocess.call(shlex.split("rm /tmp/" + xml_file))
    print("Generation has succeed")
    print("You can find your .msi at \"" + options["output"] + "\"")


# Description of cli arguments

windows_package_generator.add_param("Sources", type=str, help="Your sources directory path", default=".")
windows_package_generator.add_param("-a", "--arch", help="Architecture of the output package (x86 or x64)",
                                    default="x86")
windows_package_generator.add_param("-o", "--output", help="Output file (default : /tmp/output.msi",
                                    default="/tmp/output.msi")
windows_package_generator.add_param("-m", "--manufacturer", help="Name of the manufacturer")
windows_package_generator.add_param("-n", "--name", help="Name of the app")
windows_package_generator.add_param("-e", "--executable", help="Specify file to create shortcuts for", default=None)
windows_package_generator.add_param("--description", help="(Optional) Description", default=None)
windows_package_generator.add_param("-u", "--upgrade-code", help="The upgrade code (Auto-generate from file name if "
                                                                 "not specified", default=None)
windows_package_generator.add_param("-v", "--version", help="Version number")
windows_package_generator.add_param("-i", "--icon", help="The icon.ico path")
windows_package_generator.add_param("-d", "--install-dir", help="The installation directory name")
windows_package_generator.add_param("-r", "--root-install", help="Install program in C:/", default=False,
                                    action="store_true")
windows_package_generator.add_param("-l", "--local", help="Local user install (in AppData)", default=False,
                                    action="store_true")


def main():
    windows_package_generator.run()
    return 0


if __name__ == "__main__":
    main()
