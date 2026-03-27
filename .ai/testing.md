# Testing Patterns

## Running tests

```bash
# Via Docker (same as CI — tests must pass before final image is built)
docker build --target test .

# Locally
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/
```

The Dockerfile uses a multi-stage build: the `test` stage installs dev dependencies and runs pytest. If tests fail, the build fails and no image is produced.

## Test structure

```
tests/
  conftest.py                    # Shared autouse fixture patching module globals
  test_validate_snap_key.py      # _validate_snap_key unit tests
  test_backup_lookup.py          # _findLatestBackup + _findSpecificBackup
  test_vault_configuration.py    # loadVaultConfiguration
```

## Mocking approach

- **No moto, no freezegun** — uses `unittest.mock` only (standard library)
- `tests/conftest.py` has an `autouse` fixture that patches all module-level globals (`s3`, `bucket_name`, `captain_domain`, `backup_prefix`, `restore_this_backup`) via `monkeypatch.setattr`
- Mock paginators are constructed inline per test
- `datetime.utcnow()` is patched via `mock.patch("secret_backend.config.datetime")` with `strptime` preserved for `_validate_snap_key`

## Key patterns

### Mock paginator (simple — same response for all calls)
```python
paginator = MagicMock()
paginator.paginate.return_value = [
    {"Contents": [{"Key": "test.example.com/backups/2026-03-16/vault_2026-03-16T18:00:00.snap"}]}
]
```

### Mock paginator (prefix-aware — different responses per day)
```python
def make_paginator_by_prefix(pages_by_prefix):
    paginator = MagicMock()
    def paginate_side_effect(Bucket, Prefix):
        return pages_by_prefix.get(Prefix, [])
    paginator.paginate.side_effect = paginate_side_effect
    return paginator
```

### Freezing datetime
```python
@pytest.fixture(autouse=True)
def freeze_datetime():
    with patch("secret_backend.config.datetime") as mock_dt:
        mock_dt.utcnow.return_value.date.return_value = date(2026, 3, 16)
        mock_dt.strptime = datetime.strptime  # preserve for _validate_snap_key
        yield mock_dt
```

### Patching module globals for specific tests
```python
def test_specific_backup(self, monkeypatch):
    import secret_backend.config as config
    monkeypatch.setattr(config, "restore_this_backup", "vault_2026-03-16T18:00:00.snap")
```
