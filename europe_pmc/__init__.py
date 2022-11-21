import json
from pathlib import Path

from europe_pmc.core.api import EuropePMC


BASE_DIR = Path(__file__).resolve().parent
version_info = json.load(BASE_DIR.joinpath('version.json').open())

__version__ = version_info['version']
