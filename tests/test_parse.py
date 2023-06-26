# tests/test_parse.py
from gh_utils.parse import unparse_gh_remote_url, parse_gh_remote_url

def test_unparse_gh_remote_url():
    assert unparse_gh_remote_url("tddschn", "gh-utils", use_ssh=True) == "git@github.com:tddschn/gh-utils.git"
    assert unparse_gh_remote_url("tddschn", "gh-utils", use_ssh=False) == "https://github.com/tddschn/gh-utils.git"
    
def test_parse_gh_remote_url():
    assert parse_gh_remote_url("git@github.com:tddschn/gh-utils.git") == ("tddschn", "gh-utils", True)
    assert parse_gh_remote_url("https://github.com/tddschn/gh-utils.git") == ("tddschn", "gh-utils", False)
    assert parse_gh_remote_url("git@github.com:tddschn/gh-utils") == ("tddschn", "gh-utils", True)
    assert parse_gh_remote_url("https://github.com/tddschn/gh-utils") == ("tddschn", "gh-utils", False)
