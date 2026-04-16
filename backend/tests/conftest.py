from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
TEST_DB = ROOT / "backend/data/test_paper2lab.db"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ROOT))

os.environ["PAPER2LAB_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["PAPER2LAB_ENABLE_ONLINE_SOURCES"] = "false"

from app.core.config import get_settings

get_settings.cache_clear()

from app.core.database import Base, SessionLocal, engine
from app.main import create_app
from scripts.seed_demo import ensure_sample_pdfs, write_metadata_index


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ensure_sample_pdfs()
    write_metadata_index()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
