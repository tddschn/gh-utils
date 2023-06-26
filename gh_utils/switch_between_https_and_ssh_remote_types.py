#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2023-06-26
Purpose: Switch between HTTPS and SSH types of GitHub remotes
"""

import argparse
import subprocess
from gh_utils import __version__
from gh_utils.parse import parse_gh_remote_url, unparse_gh_remote_url


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Switch between HTTPS and SSH types of GitHub remotes',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-r', '--remote', metavar='REMOTE', type=str, default='origin', help='Name of the remote to switch'
    )
    parser.add_argument(
        '-V', '--version', action='version', version=f'%(prog)s {__version__}'
    )

    return parser.parse_args()


def main():
    """Make a jazz noise here"""

    args = get_args()
    remote_origin_url = (
            subprocess.run(['git', 'remote', 'get-url', args.remote], capture_output=True)
            .stdout.decode()
            .strip()
        )
    username, repo_name, use_ssh = parse_gh_remote_url(remote_origin_url)
    new_remote_origin_url = unparse_gh_remote_url(username, repo_name, not use_ssh)
    subprocess.run(['git', 'remote', 'set-url', args.remote, new_remote_origin_url])
    print(f'Switched remote {args.remote} from {remote_origin_url} to {new_remote_origin_url}')


if __name__ == '__main__':
    main()
