#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2022-03-24
Purpose: gh_create_repo_and_add_to_remote
"""

import argparse
from pathlib import Path
import subprocess
from . import __version__, __app_name__


class NotFoundError(Exception):
    pass


def gh_config_host_file_get_username() -> str:
    """Get authenticated user's username of gh
    from gh's config host file.

    This function was created because gh doesn't implement a way to get the username
    without making network calls.

    Returns:
        str: username
    """
    host_file_path = Path.home() / '.config/gh/hosts.yml'
    pref = '    user: '
    with open(host_file_path) as fh:
        while 1:
            line = fh.readline()
            if not line:
                break
            if line.startswith(pref):
                return line.removeprefix(pref).strip()
    raise NotFoundError(f'Username not found in {str(host_file_path)}')


# --------------------------------------------------
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
        '--overwrite_remote_origin',
        '--force',
        help='Overwrites remote origin if exists',
        action='store_true',
        default=False,
    )

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
    gh_username = gh_config_host_file_get_username()
    if remote_origin_exists:
        print('Remote origin exists.')
        if overwrite_remote_origin:
            subprocess.run(['git', 'remote', 'remove', 'origin'])
            print('Removed previous remote.')
        else:
            subprocess.run(['git', 'remote', 'rename', 'origin', 'upstream'])
            print('Renamed previous remote to upstream.')
    remote_url = f'git@github.com:{gh_username}/{repo_name}.git'
    subprocess.run(['git', 'remote', 'add', 'origin', remote_url])
    print(f'Added remote: {remote_url}')

    # create a repo on github, may fail if already exists
    subprocess.run(['gh', 'repo', 'create', repo_name, visibility_flag])


if __name__ == '__main__':
    main()
