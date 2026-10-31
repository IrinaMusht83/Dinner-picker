import tempfile
from pathlib import Path

import pytest

import db.profiles as profiles_mod


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    tmp = Path(tempfile.mkdtemp()) / "test.sqlite"
    monkeypatch.setattr(profiles_mod, "DB_PATH", tmp)
    profiles_mod.init_db()
    yield tmp


def test_save_and_get():
    profiles_mod.save_profile(1, "chizhik_test_001", 3)
    p = profiles_mod.get_profile(1)
    assert p["store_id"] == "chizhik_test_001"
    assert p["default_persons"] == 3


def test_get_missing():
    assert profiles_mod.get_profile(999) is None


def test_upsert():
    profiles_mod.save_profile(1, "chizhik_test_001", 2)
    profiles_mod.save_profile(1, "chizhik_test_001", 5)
    assert profiles_mod.get_profile(1)["default_persons"] == 5


def test_invalid_persons():
    with pytest.raises(ValueError):
        profiles_mod.save_profile(1, "chizhik_test_001", 0)
    with pytest.raises(ValueError):
        profiles_mod.save_profile(1, "chizhik_test_001", 21)