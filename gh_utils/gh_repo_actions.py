#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2025-12-01
Purpose: Manage GitHub Actions permissions with gh CLI.
"""

import argparse
import subprocess

from gh_utils import __version__
from gh_utils.parse import parse_gh_remote_url


ACCEPT_HEADER = "Accept: application/vnd.github+json"
ACTIONS_PERMISSIONS_TEMPLATE = "repos/{owner}/{repo}/actions/permissions"


def get_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Inspect or toggle GitHub Actions permissions for the current repository",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="get",
        choices=["get", "disable", "enable"],
        help="Operation to perform",
    )
    parser.add_argument(
        "-r",
        "--remote",
        metavar="REMOTE",
        default="origin",
        help="Remote to derive OWNER/REPO from",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def get_owner_and_repo(remote: str) -> tuple[str, str]:
    """Read the git remote URL and parse owner/repo from it."""

    remote_origin_url = (
        subprocess.run(
            ["git", "remote", "get-url", remote], capture_output=True, check=True
        )
        .stdout.decode()
        .strip()
    )
    username, repo_name, _ = parse_gh_remote_url(remote_origin_url)
    return username, repo_name


def build_api_path(owner: str, repo: str) -> str:
    return ACTIONS_PERMISSIONS_TEMPLATE.format(owner=owner, repo=repo)


def run_get(owner: str, repo: str) -> None:
    path = build_api_path(owner, repo)
    subprocess.run(["gh", "api", "-H", ACCEPT_HEADER, path], check=True)


def run_toggle(owner: str, repo: str, enabled: bool) -> None:
    path = build_api_path(owner, repo)
    enabled_value = "true" if enabled else "false"
    subprocess.run(
        [
            "gh",
            "api",
            "--method",
            "PUT",
            path,
            "--field",
            f"enabled={enabled_value}",
            "-H",
            ACCEPT_HEADER,
        ],
        check=True,
    )


def main() -> None:
    args = get_args()
    owner, repo = get_owner_and_repo(args.remote)

    if args.command == "get":
        run_get(owner, repo)
    elif args.command == "disable":
        run_toggle(owner, repo, enabled=False)
    else:
        run_toggle(owner, repo, enabled=True)


if __name__ == "__main__":
    main()
