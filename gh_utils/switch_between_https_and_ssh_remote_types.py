#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2023-06-26
Purpose: Switch between HTTPS and SSH types of GitHub remotes
"""

import argparse
from pathlib import Path


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Switch between HTTPS and SSH types of GitHub remotes',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    return parser.parse_args()


def main():
    """Make a jazz noise here"""

    args = get_args()


if __name__ == '__main__':
    main()
