import logging, logging.config
import os

import yaml
from flask import Flask
from dotenv import load_dotenv

LOGGING_CONFIG = "logging.yaml"
ENV_FILE = ".env"
load_dotenv(ENV_FILE)
API_PASSWORD = os.environ["API_PASSWORD"]


def _setup_logging() -> logging.Logger:
    with open(LOGGING_CONFIG) as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)

    return logging.getLogger(__name__)


log = _setup_logging()


def create_app() -> Flask:
    log.info("Creating Flask app")

    return Flask(__name__)


app = create_app()

import pihole_disable.views
