# Common Pitfalls

## Module-level globals in config.py

`s3`, `bucket_name`, `captain_domain`, `backup_prefix`, and `restore_this_backup` are set at import time from environment variables. When writing tests, always patch via `monkeypatch.setattr` on the module attribute, not on env vars. The `conftest.py` `autouse` fixture handles this automatically.

## Asymmetric error handling in loadVaultConfiguration

`loadVaultConfiguration` first calls `configFileExists()`, which re-raises S3 errors (they propagate to callers). If the file exists but the subsequent `get_object` call fails, it returns `None`. Invalid JSON raises `ValueError`. This is intentional — existence-check failures propagate so callers can skip init safely, `get_object` failures are treated as retryable, and corrupt config is a fatal condition.

## configFileExists checks the wrong key

`configFileExists()` always checks the global `file_key` (`vault_access.json`), not the `file_name` parameter passed to `loadVaultConfiguration`. This is a known limitation. If `loadVaultConfiguration` is called with a different filename, the existence check may give a wrong answer.

## Never swallow S3 exceptions in backup discovery

The original bug was: `getLatestBackupfromS3()` caught all S3 exceptions and returned `None`, which `main.py` interpreted as "no backup exists" and triggered a fresh vault init — destroying existing data. All S3 exceptions in backup discovery must re-raise.

## Never log vault secrets

Vault config files contain unseal keys and root tokens. JSON parse error messages intentionally omit the exception detail to avoid leaking JSON fragments that could contain secrets. S3 error messages (e.g. from `get_object` failures) do include `{str(e)}` since S3 exceptions don't contain vault secrets.

## ENABLE_RESTORE is case-insensitive

Normalized with `.lower()` at startup. All comparisons use `== "true"`. If adding new env var checks, follow the same pattern.

## CAPTAIN_DOMAIN must be set when restore is enabled

Validated at startup in `main.py`. If missing, `sys.exit(1)`. Without this, S3 prefix construction produces `None/hashicorp-vault-backups/...` which silently queries the wrong path.
