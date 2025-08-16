import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from audiostats.db.models import Base

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def test_sessionmaker(test_engine):
    sessionfactory = sessionmaker(bind=test_engine)
    logger.debug(f'session type: {type(sessionfactory)}')
    return sessionfactory