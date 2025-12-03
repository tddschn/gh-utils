#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2025-12-01
Purpose: Manage GitHub Actions permissions with gh CLI.
"""

import argparse
import shlex
import subprocess
from typing import cast

from gh_utils import __version__
from gh_utils.parse import parse_gh_remote_url


ACCEPT_HEADER = "Accept: application/vnd.github+json"
ACTIONS_PERMISSIONS_TEMPLATE = "repos/{owner}/{repo}/actions/permissions"


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
        "-n",
        "--dry-run",
        help="Show the commands that would run without executing them",
        action="store_true",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def get_owner_and_repo(remote: str, *, dry_run: bool) -> tuple[str, str]:
    """Read the git remote URL and parse owner/repo from it."""

    remote_origin_url = cast(
        str,
        run_command(
            ["git", "remote", "get-url", remote],
            capture_output=True,
            text=True,
            check=True,
            dry_run=dry_run,
            mutating=False,
        ).stdout.strip(),
    )
    username, repo_name, _ = parse_gh_remote_url(remote_origin_url)
    return username, repo_name


def build_api_path(owner: str, repo: str) -> str:
    return ACTIONS_PERMISSIONS_TEMPLATE.format(owner=owner, repo=repo)


def run_get(owner: str, repo: str, *, dry_run: bool) -> None:
    path = build_api_path(owner, repo)
    run_command(["gh", "api", "-H", ACCEPT_HEADER, path], check=True, dry_run=dry_run)


def run_toggle(owner: str, repo: str, enabled: bool, *, dry_run: bool) -> None:
    path = build_api_path(owner, repo)
    enabled_value = "true" if enabled else "false"
    run_command(
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
        dry_run=dry_run,
    )


def main() -> None:
    args = get_args()
    owner, repo = get_owner_and_repo(args.remote, dry_run=args.dry_run)

    if args.command == "get":
        run_get(owner, repo, dry_run=args.dry_run)
    elif args.command == "disable":
        run_toggle(owner, repo, enabled=False, dry_run=args.dry_run)
    else:
        run_toggle(owner, repo, enabled=True, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
