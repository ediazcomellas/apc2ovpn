#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#This program opens an .apc file and converts its to .ovpn format.
#

import argparse
import json
import os

# Translate "sophos" variable names to "openvpn"
translation_table = {
    "protocol": "proto",
    "certificate": "cert",
    "ca_cert": "ca",
    "encryption_algorithm": "cipher",
    "server_address": "remote",
    "authentication_algorithm": "auth",
    "server_dn": "verify-x509-name"
    # otros mapeos pueden ir aquí, en formato "clave original": "nueva clave"
}


def load_json_file(input_file_name, output_file_name, output_authfile_name):
    with open(input_file_name, 'r') as file:
        data = json.load(file)

    output_data = {}
    remotes = None
    server_port = None
    # Get all variables and translate them
    #Pay attention to remotes and port, which are handled differently
    for key, value in data.items():
        new_key = translation_table.get(key, key)  # check in translation table
        if new_key == "server_port":
            server_port = value
        elif new_key == "remote":
            if isinstance(value, list):  # check if remotes is a list (always is)
                remotes = value
        else:
            output_data[new_key] = value

    # Generates two list of lines to append. One for variables and other for certificates
    lines = []
    lines.append(f"# {output_file_name}")
    lines.append(f"client")
    lines.append(f"dev tun")

    lines2 = []

    for key, value in output_data.items():
        if key in ["cert", "key", "ca"]:
            lines2.append(f'<{key}>\n{value}\n</{key}>')
        elif key == "verify-x509-name":
            lines.append(f'{key} "{value}"')  # this variable must be doublequoted
        elif key in ["username","password"]:
            lines.append(f'#{key} {value}')
        else:
            lines.append(f'{key} {value}')  # uses space as delimiter

    # create the "remote" lines
    if remotes is not None and server_port is not None:
        for remote in remotes:
            lines.append(f'remote {remote} {server_port}')

    # save the .ovpn file
    with open(output_file_name, 'w') as file:
        file.write('\n'.join(lines))
        if "username" in output_data.keys():
            file.write(f"\n\nauth-user-pass {output_authfile_name}")
        file.write('\n\n')
        file.write('\n'.join(lines2))

    # save the .pass file.
    if "username" in output_data.keys():
        with open(output_authfile_name, 'w') as file:
            file.write(f"{output_data['username']}")
            file.write(f"\n{output_data['password']}")



parser = argparse.ArgumentParser(description='Convert Sophos APC files to native openvpn format',
                                 epilog="Use at your own risk!. Please check the output files")

parser.add_argument('-i', required=True, help='Name of the JSON formatted file to load (.apc)')
parser.add_argument('-o', default=None, help='Nombre del archivo de salida, si se especifica')

args = parser.parse_args()

if args.o:
    output_file_name = args.o
    output_authfile_name = os.path.splitext(args.o)[0] + '.pass'
else:
    output_file_name = os.path.splitext(args.i)[0] + '.ovpn'
    output_authfile_name = os.path.splitext(args.i)[0] + '.pass'

load_json_file(args.i, output_file_name,output_authfile_name)
