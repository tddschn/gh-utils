#!/usr/bin/env python3

from . import NotFoundError
from pathlib import Path

DEFAULT_GH_CONFIG_DIR_UNIX = Path.home() / '.config/gh'
DEFAULT_GH_CONFIG_DIR_WINDOWS = Path.home() / 'Appdata/Roaming/GitHub CLI'

if DEFAULT_GH_CONFIG_DIR_UNIX.exists():
    DEFAULT_GH_CONFIG_DIR = DEFAULT_GH_CONFIG_DIR_UNIX
elif DEFAULT_GH_CONFIG_DIR_WINDOWS.exists():
    DEFAULT_GH_CONFIG_DIR = DEFAULT_GH_CONFIG_DIR_WINDOWS
else:
    raise NotFoundError('No GitHub CLI config directory found')

DEFAULT_GH_CONFIG_YML_PATH = DEFAULT_GH_CONFIG_DIR / 'config.yml'
DEFAULT_GH_HOSTS_YML_PATH = DEFAULT_GH_CONFIG_DIR / 'hosts.yml'
