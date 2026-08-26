import logging
import logging.config
import os
from pathlib import Path

import yaml
from quart import Quart
from dotenv import load_dotenv

LOGGING_CONFIG = "logging.yaml"
if Path(".docker").exists():
    LOGGING_CONFIG = "logging_docker.yaml"
ENV_FILE = ".env"
load_dotenv(ENV_FILE)
API_URL = os.environ["API_URL"]
API_PASSWORD = os.environ["API_PASSWORD"]


def _setup_logging() -> logging.Logger:
    with open(LOGGING_CONFIG) as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)

    return logging.getLogger(__name__)


log = _setup_logging()


def create_app() -> Quart:
    log.info("======================")
    log.info("=== PIHOLE-DISABLE ===")
    log.info("======================")
    log.info("Creating Quart (Flask) app")

    return Quart(__name__)


app = create_app()

import pihole_disable.views
