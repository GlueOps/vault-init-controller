import pytest
from secret_backend.config import _validate_snap_key


class TestValidSnapKeys:
    def test_standard_key(self):
        assert _validate_snap_key("example.com/hashicorp-vault-backups/2026-03-16/vault_2026-03-16T18:00:00.snap") is True

    def test_midnight(self):
        assert _validate_snap_key("example.com/backups/2026-01-01/vault_2026-01-01T00:00:00.snap") is True

    def test_end_of_day(self):
        assert _validate_snap_key("example.com/backups/2026-12-31/vault_2026-12-31T23:59:59.snap") is True

    def test_leap_year_feb_29(self):
        assert _validate_snap_key("example.com/backups/2024-02-29/vault_2024-02-29T12:00:00.snap") is True

    def test_deep_prefix(self):
        assert _validate_snap_key("a/b/c/d/2026-03-16/vault_2026-03-16T18:00:00.snap") is True


class TestInvalidSnapKeys:
    def test_non_padded_month(self):
        assert _validate_snap_key("example.com/backups/2026-3-16/vault_2026-3-16T18:00:00.snap") is False

    def test_non_padded_day(self):
        assert _validate_snap_key("example.com/backups/2026-03-6/vault_2026-03-06T18:00:00.snap") is False

    def test_non_padded_hour(self):
        assert _validate_snap_key("example.com/backups/2026-03-16/vault_2026-03-16T8:00:00.snap") is False

    def test_impossible_month(self):
        assert _validate_snap_key("example.com/backups/2026-13-01/vault_2026-13-01T18:00:00.snap") is False

    def test_impossible_day(self):
        assert _validate_snap_key("example.com/backups/2026-02-30/vault_2026-02-30T18:00:00.snap") is False

    def test_non_leap_year_feb_29(self):
        assert _validate_snap_key("example.com/backups/2026-02-29/vault_2026-02-29T18:00:00.snap") is False

    def test_directory_file_date_mismatch(self):
        assert _validate_snap_key("example.com/backups/2026-03-15/vault_2026-03-16T18:00:00.snap") is False

    def test_space_separator_instead_of_T(self):
        assert _validate_snap_key("example.com/backups/2026-03-16/vault_2026-03-16 18:00:00.snap") is False

    def test_wrong_field_order(self):
        assert _validate_snap_key("example.com/backups/16-03-2026/vault_16-03-2026T18:00:00.snap") is False

    def test_missing_snap_extension(self):
        assert _validate_snap_key("example.com/backups/2026-03-16/vault_2026-03-16T18:00:00") is False

    def test_no_prefix(self):
        assert _validate_snap_key("2026-03-16/vault_2026-03-16T18:00:00.snap") is False

    def test_empty_string(self):
        assert _validate_snap_key("") is False

    def test_just_snap_extension(self):
        assert _validate_snap_key("something.snap") is False

    def test_invalid_hour(self):
        assert _validate_snap_key("example.com/backups/2026-03-16/vault_2026-03-16T25:00:00.snap") is False

    def test_invalid_minute(self):
        assert _validate_snap_key("example.com/backups/2026-03-16/vault_2026-03-16T18:61:00.snap") is False

    def test_invalid_second(self):
        assert _validate_snap_key("example.com/backups/2026-03-16/vault_2026-03-16T18:00:61.snap") is False
