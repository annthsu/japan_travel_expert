"""Basic config

To set project basic config
"""

from pathlib import Path
import os

# Project path
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
# Log folder path
LOG_PATH = PROJECT_PATH + '/log'
# Create log folder if log folder is not exist
Path(LOG_PATH).mkdir(parents=False, exist_ok=True)
