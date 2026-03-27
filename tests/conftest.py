import pytest
from unittest.mock import MagicMock
import secret_backend.config as secret_config


@pytest.fixture(autouse=True)
def mock_config_globals(monkeypatch):
    mock_s3 = MagicMock()
    monkeypatch.setattr(secret_config, "s3", mock_s3)
    monkeypatch.setattr(secret_config, "bucket_name", "test-bucket")
    monkeypatch.setattr(secret_config, "captain_domain", "test.example.com")
    monkeypatch.setattr(secret_config, "backup_prefix", "hashicorp-vault-backups")
    monkeypatch.setattr(secret_config, "restore_this_backup", None)
    return mock_s3


def make_snap_obj(key):
    return {"Key": key}
