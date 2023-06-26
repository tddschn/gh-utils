import re

def unparse_gh_remote_url(username: str, repo_name: str, use_ssh=False) -> str:
    if use_ssh:
        return f"git@github.com:{username}/{repo_name}.git"
    else:
        return f"https://github.com/{username}/{repo_name}.git"


def parse_gh_remote_url(gh_remote_url: str) -> tuple[str, str, bool]:
    pattern = re.compile(r"(?:https?://github\.com/|git@github\.com:)([^/]+)/(.+)(\.git)?")
    match = pattern.match(gh_remote_url)
    if match:
        return match.group(1), match.group(2).removesuffix('.git'), gh_remote_url.startswith('git@')
    else:
        raise ValueError("Invalid GitHub remote URL")
