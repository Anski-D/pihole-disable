import logging

import pytest

import pihole_disable


def _setup_logging() -> logging.Logger:
    log = logging.getLogger()
    log.setLevel(logging.NOTSET)
    log.addHandler(logging.NullHandler())

    return log


@pytest.fixture(autouse=True)
def patch_init(monkeypatch):
    monkeypatch.setattr(pihole_disable, "log", lambda: _setup_logging())
