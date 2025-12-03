#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2023-06-26
Purpose: Switch between HTTPS and SSH types of GitHub remotes
"""

import argparse
import shlex
import subprocess
from typing import cast
from gh_utils import __version__
from gh_utils.parse import parse_gh_remote_url, unparse_gh_remote_url


def _format_command(cmd: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in cmd)


def run_command(
    cmd: list[str],
    *,
    dry_run: bool,
    mutating: bool = True,
    **kwargs,
):
    printable = _format_command(cmd)
    if dry_run:
        if mutating:
            print(f"[dry-run] Would run: {printable}")
            if kwargs.get("capture_output"):
                empty = "" if kwargs.get("text") else b""
                return subprocess.CompletedProcess(cmd, 0, stdout=empty, stderr=empty)
            return subprocess.CompletedProcess(cmd, 0)
        print(f"[dry-run] Inspecting state with: {printable}")
    return subprocess.run(cmd, **kwargs)


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Switch between HTTPS and SSH types of GitHub remotes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-r",
        "--remote",
        metavar="REMOTE",
        type=str,
        default="origin",
        help="Name of the remote to switch",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        help="Show the commands that would run without changing the remote",
        action="store_true",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


def main():
    """Make a jazz noise here"""

    args = get_args()
    remote_origin_url = cast(
        str,
        run_command(
            ["git", "remote", "get-url", args.remote],
            capture_output=True,
            text=True,
            dry_run=args.dry_run,
            mutating=False,
        ).stdout.strip(),
    )
    username, repo_name, use_ssh = parse_gh_remote_url(remote_origin_url)
    new_remote_origin_url = unparse_gh_remote_url(username, repo_name, not use_ssh)
    run_command(
        ["git", "remote", "set-url", args.remote, new_remote_origin_url],
        dry_run=args.dry_run,
    )
    action = "Would switch" if args.dry_run else "Switched"
    print(
        f"{action} remote {args.remote} from {remote_origin_url} to {new_remote_origin_url}"
    )


if __name__ == "__main__":
    main()
