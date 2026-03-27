import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch
from secret_backend.config import (
    _findLatestBackup,
    _findSpecificBackup,
    BackupNotFoundError,
)
from tests.conftest import make_snap_obj

DOMAIN = "test.example.com"
PREFIX = "hashicorp-vault-backups"
FROZEN_DATE = date(2026, 3, 16)


def make_paginator(pages):
    paginator = MagicMock()
    paginator.paginate.return_value = pages
    return paginator


def make_paginator_by_prefix(pages_by_prefix):
    paginator = MagicMock()

    def paginate_side_effect(Bucket, Prefix):
        return pages_by_prefix.get(Prefix, [])

    paginator.paginate.side_effect = paginate_side_effect
    return paginator


def snap_key(date_str, time_str):
    return f"{DOMAIN}/{PREFIX}/{date_str}/vault_{date_str}T{time_str}.snap"


@pytest.fixture(autouse=True)
def freeze_datetime():
    with patch("secret_backend.config.datetime") as mock_dt:
        mock_dt.utcnow.return_value.date.return_value = FROZEN_DATE
        mock_dt.strptime = datetime.strptime
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        yield mock_dt


class TestFindLatestBackupSuccess:
    def test_today_has_one_snap(self):
        key = snap_key("2026-03-16", "18:00:00")
        pages = [{"Contents": [make_snap_obj(key)]}]
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": pages,
        })
        result = _findLatestBackup(paginator)
        assert result["Key"] == key

    def test_multi_page_returns_last_snap(self):
        key1 = snap_key("2026-03-16", "08:00:00")
        key2 = snap_key("2026-03-16", "18:00:00")
        pages = [
            {"Contents": [make_snap_obj(key1)]},
            {"Contents": [make_snap_obj(key2)]},
        ]
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": pages,
        })
        result = _findLatestBackup(paginator)
        assert result["Key"] == key2

    def test_skips_non_snap_files(self):
        snap = snap_key("2026-03-16", "18:00:00")
        pages = [{"Contents": [
            make_snap_obj(f"{DOMAIN}/{PREFIX}/2026-03-16/some_file.json"),
            make_snap_obj(snap),
        ]}]
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": pages,
        })
        result = _findLatestBackup(paginator)
        assert result["Key"] == snap

    def test_falls_back_to_earlier_day(self):
        key = snap_key("2026-03-13", "12:00:00")
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": [],
            f"{DOMAIN}/{PREFIX}/2026-03-15/": [],
            f"{DOMAIN}/{PREFIX}/2026-03-14/": [],
            f"{DOMAIN}/{PREFIX}/2026-03-13/": [{"Contents": [make_snap_obj(key)]}],
        })
        result = _findLatestBackup(paginator)
        assert result["Key"] == key

    def test_day_44_boundary_included(self):
        target_date = date(2026, 1, 31)  # 44 days before 2026-03-16
        key = f"{DOMAIN}/{PREFIX}/{target_date.isoformat()}/vault_{target_date.isoformat()}T12:00:00.snap"
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/{target_date.isoformat()}/": [{"Contents": [make_snap_obj(key)]}],
        })
        result = _findLatestBackup(paginator)
        assert result["Key"] == key

    def test_verifies_correct_prefix_format(self):
        paginator = make_paginator_by_prefix({})
        _findLatestBackup(paginator)
        call_args = [c.kwargs["Prefix"] for c in paginator.paginate.call_args_list]
        assert call_args[0] == f"{DOMAIN}/{PREFIX}/2026-03-16/"
        assert call_args[1] == f"{DOMAIN}/{PREFIX}/2026-03-15/"
        assert call_args[-1] == f"{DOMAIN}/{PREFIX}/2026-01-31/"
        assert len(call_args) == 45


class TestFindLatestBackupFailure:
    def test_no_backups_in_45_days(self):
        paginator = make_paginator_by_prefix({})
        result = _findLatestBackup(paginator)
        assert result is None

    def test_page_without_contents_key(self):
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": [{}],
        })
        result = _findLatestBackup(paginator)
        assert result is None

    def test_invalid_snap_key_raises_value_error(self):
        bad_key = f"{DOMAIN}/{PREFIX}/2026-03-16/vault_bad-format.snap"
        pages = [{"Contents": [make_snap_obj(bad_key)]}]
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": pages,
        })
        with pytest.raises(ValueError, match="does not match expected date format"):
            _findLatestBackup(paginator)

    def test_valid_then_invalid_snap_raises_value_error(self):
        valid_key = snap_key("2026-03-16", "08:00:00")
        bad_key = f"{DOMAIN}/{PREFIX}/2026-03-16/vault_bad.snap"
        pages = [{"Contents": [
            make_snap_obj(valid_key),
            make_snap_obj(bad_key),
        ]}]
        paginator = make_paginator_by_prefix({
            f"{DOMAIN}/{PREFIX}/2026-03-16/": pages,
        })
        with pytest.raises(ValueError, match="does not match expected date format"):
            _findLatestBackup(paginator)


class TestFindSpecificBackupSuccess:
    def test_matching_filename_found(self, monkeypatch):
        import secret_backend.config as config
        monkeypatch.setattr(config, "restore_this_backup", "vault_2026-03-16T18:00:00.snap")
        key = snap_key("2026-03-16", "18:00:00")
        paginator = make_paginator([{"Contents": [make_snap_obj(key)]}])
        result = _findSpecificBackup(paginator)
        assert result["Key"] == key

    def test_match_on_second_page(self, monkeypatch):
        import secret_backend.config as config
        monkeypatch.setattr(config, "restore_this_backup", "vault_2026-03-10T12:00:00.snap")
        key = snap_key("2026-03-10", "12:00:00")
        paginator = make_paginator([
            {"Contents": [make_snap_obj(snap_key("2026-03-16", "18:00:00"))]},
            {"Contents": [make_snap_obj(key)]},
        ])
        result = _findSpecificBackup(paginator)
        assert result["Key"] == key


class TestFindSpecificBackupFailure:
    def test_not_found_raises_backup_not_found_error(self, monkeypatch):
        import secret_backend.config as config
        monkeypatch.setattr(config, "restore_this_backup", "nonexistent.snap")
        paginator = make_paginator([{"Contents": [
            make_snap_obj(snap_key("2026-03-16", "18:00:00")),
        ]}])
        with pytest.raises(BackupNotFoundError, match="no matching backup"):
            _findSpecificBackup(paginator)

    def test_skips_non_snap_with_matching_basename(self, monkeypatch):
        import secret_backend.config as config
        monkeypatch.setattr(config, "restore_this_backup", "vault_2026-03-16T18:00:00.json")
        paginator = make_paginator([{"Contents": [
            make_snap_obj(f"{DOMAIN}/{PREFIX}/2026-03-16/vault_2026-03-16T18:00:00.json"),
        ]}])
        with pytest.raises(BackupNotFoundError):
            _findSpecificBackup(paginator)

    def test_invalid_key_format_on_match_raises_value_error(self, monkeypatch):
        import secret_backend.config as config
        monkeypatch.setattr(config, "restore_this_backup", "vault_bad-format.snap")
        bad_key = f"{DOMAIN}/{PREFIX}/2026-03-16/vault_bad-format.snap"
        paginator = make_paginator([{"Contents": [make_snap_obj(bad_key)]}])
        with pytest.raises(ValueError, match="does not match expected date format"):
            _findSpecificBackup(paginator)
