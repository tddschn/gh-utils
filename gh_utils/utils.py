#!/usr/bin/env python3


from functools import cache
from pathlib import Path

from .config import DEFAULT_GH_CONFIG_YML_PATH, DEFAULT_GH_HOSTS_YML_PATH
from .types import UserInfo
from . import NotFoundError


@cache
def gh_config_yaml_get_user_info(
    gh_hosts_yaml: Path = DEFAULT_GH_HOSTS_YML_PATH,
) -> list[UserInfo]:
    from yaml import safe_load

    user_info_list: list[UserInfo] = []
    hosts_d = safe_load(gh_hosts_yaml.read_text())
    for hostname, info in hosts_d.items():
        user_info_list.append(UserInfo(hostname=hostname, user=info['user']))
    return user_info_list


def gh_config_yaml_get_user_info_first(
    gh_hosts_yaml: Path = DEFAULT_GH_HOSTS_YML_PATH,
) -> UserInfo:
    user_info_list = gh_config_yaml_get_user_info(gh_hosts_yaml)
    if user_info_list:
        return user_info_list[0]
    else:
        raise NotFoundError(f'No user info found in {str(gh_hosts_yaml)}')


@cache
def gh_config_yaml_get_first_hostname_and_username(
    gh_hosts_yaml: Path = DEFAULT_GH_HOSTS_YML_PATH,
) -> tuple[str, str]:
    user_info = gh_config_yaml_get_user_info_first(gh_hosts_yaml)
    return user_info['hostname'], user_info['user']


def hostname_to_user(
    hostname: str, gh_hosts_yaml: Path = DEFAULT_GH_HOSTS_YML_PATH
) -> str:
    for user_info in gh_config_yaml_get_user_info(gh_hosts_yaml):
        if user_info['hostname'] == hostname:
            return user_info['user']
    else:
        raise NotFoundError(f'No user info found for hostname {hostname}')
