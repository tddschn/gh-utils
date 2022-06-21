#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2022-03-24
Purpose: gh_create_repo_and_add_to_remote
"""

import argparse
from pathlib import Path
import subprocess
from . import __version__, NotFoundError
from .utils import (
    gh_config_yaml_get_user_info,
    gh_config_yaml_get_user_info_first,
    gh_config_yaml_get_first_hostname_and_username,
    hostname_to_user,
)

__app_name__ = 'ghcrar'


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description='Create a GitHub repo with gh and add it as a remote',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-a',
        '--append',
        help='String to append to the repo name',
        metavar='SUFFIX',
        type=str,
        default=None,
    )

    parser.add_argument(
        '-n',
        '--name',
        help='The string to use as GitHub repo name',
        metavar='GITHUB REPO NAME',
        type=str,
        default=None,
    )

    parser.add_argument(
        '--public',
        help='Create a public repository',
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '--overwrite-remote-origin',
        '--force',
        help='Overwrites remote origin if exists',
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '-H',
        '--hostname',
        help='GitHub hostname, default to use the first entry in hosts.yml',
        default=gh_config_yaml_get_first_hostname_and_username()[0],
        choices=['ssh', 'https'],
    )

    parser.add_argument('-p', '--protocol', help='git protocol', default='ssh')
    parser.add_argument(
        '-V', '--version', action='version', version=f'%(prog)s {__version__}'
    )

    return parser.parse_args()


def main():
    args = get_args()
    append = args.append
    name = args.name
    public = args.public
    overwrite_remote_origin = args.overwrite_remote_origin
    hostname = args.hostname
    protocol = args.protocol

    curr_path_name = Path.cwd().name
    if name is not None:
        repo_name = name
    else:
        repo_name = curr_path_name if append is None else f'{curr_path_name}-{append}'
    visibility_flag = '--public' if public else '--private'

    # (re) init the repo
    subprocess.run(['git', 'init'])

    # add to remote
    remotes_p = subprocess.run(['git', 'remote'], capture_output=True)
    remotes = remotes_p.stdout.splitlines()
    # print(remotes)
    remote_origin_exists = b'origin' in remotes
    gh_username = hostname_to_user(hostname)
    if remote_origin_exists:
        print('Remote origin exists.')
        if overwrite_remote_origin:
            subprocess.run(['git', 'remote', 'remove', 'origin'])
            print('Removed previous remote.')
        else:
            subprocess.run(['git', 'remote', 'rename', 'origin', 'upstream'])
            print('Renamed previous remote to upstream.')
    if protocol == 'ssh':
        remote_url_prefix = f'git@{hostname}:'
    elif protocol == 'https':
        remote_url_prefix = f'https://{hostname}/'
    else:
        raise ValueError(f'Unknown protocol: {protocol}')
    remote_url = f'{remote_url_prefix}{gh_username}/{repo_name}.git'
    subprocess.run(['git', 'remote', 'add', 'origin', remote_url])
    print(f'Added remote: {remote_url}')

    # create a repo on github, may fail if already exists
    subprocess.run(['gh', 'repo', 'create', repo_name, visibility_flag])


if __name__ == '__main__':
    main()
