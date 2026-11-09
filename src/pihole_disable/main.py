import logging
import logging.config
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from quart import Quart

LOGGING_CONFIG = "logging_docker.yaml" if Path(".docker").exists() else "logging.yaml"
ENV_FILE = ".env"
load_dotenv(ENV_FILE)
API_URL = os.environ["API_URL"]
API_PASSWORD = os.environ["API_PASSWORD"]


def _setup_logging() -> logging.Logger:
    with open(LOGGING_CONFIG) as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)

    return logging.getLogger(__package__)


log = _setup_logging()


def create_app() -> Quart:
    log.info("======================")
    log.info("=== PIHOLE-DISABLE ===")
    log.info("======================")
    log.info("Creating Quart (Flask) app")

    return Quart(__name__)


app = create_app()

import pihole_disable.views  # noqa: F401

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
