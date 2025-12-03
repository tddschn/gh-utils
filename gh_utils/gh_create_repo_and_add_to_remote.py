#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2022-03-24
Purpose: gh_create_repo_and_add_to_remote
"""

import argparse
import shlex
import subprocess
from functools import cache
from pathlib import Path
from typing import cast
from gh_utils import __version__
from gh_utils.utils import (
    gh_config_yaml_get_first_hostname_and_username,
    hostname_to_user,
)

__app_name__ = "ghcrar"


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
        prog=__app_name__,
        description="Create a GitHub repo with gh and add it as a remote",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-a",
        "--append",
        help="String to append to the repo name",
        metavar="SUFFIX",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-N",
        "--name",
        help="The string to use as GitHub repo name, or <user|org>/<repo-name> with a slash",
        metavar="GITHUB REPO NAME",
        type=str,
        default=None,
    )

    # -r, --remote string          Specify remote name for the new repository
    parser.add_argument(
        "-r",
        "--remote",
        help="Specify remote name for the new repository",
        type=str,
        default="origin",
    )

    parser.add_argument(
        "--public",
        help="Create a public repository",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--overwrite-remote",
        "--force",
        help="Overwrites remote if exists",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-H",
        "--hostname",
        help="GitHub hostname, default to use the first entry in hosts.yml",
        default=gh_config_yaml_get_first_hostname_and_username()[0],
        choices=["ssh", "https"],
    )

    parser.add_argument("-p", "--protocol", help="git protocol", default="ssh")
    parser.add_argument(
        "-S",
        "--no-set-default",
        help="Do not run `gh repo set-default`",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        help="Show commands without executing changes",
        action="store_true",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


def main():
    args = get_args()
    append = args.append
    name = args.name
    public = args.public
    overwrite_remote_origin = args.overwrite_remote
    hostname = args.hostname
    protocol = args.protocol
    desired_remote_name = args.remote
    dry_run = args.dry_run

    curr_path_name = Path.cwd().name
    if name is not None:
        repo_name = name
    else:
        repo_name = curr_path_name if append is None else f"{curr_path_name}-{append}"
    visibility_flag = "--public" if public else "--private"

    # (re) init the repo
    run_command(["git", "init"], dry_run=dry_run)

    # add to remote
    remotes_p = run_command(
        ["git", "remote"],
        capture_output=True,
        text=True,
        dry_run=dry_run,
        mutating=False,
    )
    remotes = remotes_p.stdout.splitlines()
    # print(remotes)
    remote_origin_exists = desired_remote_name in remotes
    gh_username = hostname_to_user(hostname)
    desired_remote_url = get_desired_remote_url(
        hostname, protocol, repo_name, gh_username
    )
    if remote_origin_exists:
        print(f"Remote {desired_remote_name} exists.")
        # run `git remote get-url origin` to get the url for the remote
        remote_origin_url = cast(
            str,
            run_command(
                ["git", "remote", "get-url", desired_remote_name],
                capture_output=True,
                text=True,
                dry_run=dry_run,
                mutating=False,
            ).stdout.strip(),
        )
        if remote_origin_url.removesuffix(".git") == desired_remote_url.removesuffix(
            ".git"
        ):
            print(
                f"Remote {desired_remote_name} URL {remote_origin_url} is already the desired one."
            )
            print("Exiting.")
            return
        if overwrite_remote_origin:
            run_command(
                ["git", "remote", "remove", desired_remote_name], dry_run=dry_run
            )
            print("Removed previous remote.")
        else:
            run_command(
                ["git", "remote", "rename", desired_remote_name, "upstream"],
                dry_run=dry_run,
            )
            print("Renamed previous remote to upstream.")
    run_command(
        ["git", "remote", "add", desired_remote_name, desired_remote_url],
        dry_run=dry_run,
    )
    print(f"Added remote: {desired_remote_url}")

    # create a repo on github, may fail if already exists
    run_command(["gh", "repo", "create", repo_name, visibility_flag], dry_run=dry_run)

    if not args.no_set_default:
        print(f"Running `gh repo set-default {gh_username}/{repo_name}`")
        run_command(
            ["gh", "repo", "set-default", f"{gh_username}/{repo_name}"],
            dry_run=dry_run,
        )


@cache
def get_desired_remote_url(
    hostname: str, protocol: str, repo_name: str, gh_username: str
) -> str:
    if protocol == "ssh":
        remote_url_prefix = f"git@{hostname}:"
    elif protocol == "https":
        remote_url_prefix = f"https://{hostname}/"
    else:
        raise ValueError(f"Unknown protocol: {protocol}")
    if "/" not in repo_name:
        remote_url = f"{remote_url_prefix}{gh_username}/{repo_name}.git"
    else:
        remote_url = f"{remote_url_prefix}{repo_name}.git"
    return remote_url


if __name__ == "__main__":
    main()
