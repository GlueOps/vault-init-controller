# Common Pitfalls

## Module-level globals in config.py

`s3`, `bucket_name`, `captain_domain`, `backup_prefix`, and `restore_this_backup` are set at import time from environment variables. When writing tests, always patch via `monkeypatch.setattr` on the module attribute, not on env vars. The `conftest.py` `autouse` fixture handles this automatically.

## Asymmetric error handling in loadVaultConfiguration

S3 errors return `None`, but invalid JSON raises `ValueError`. This is intentional — S3 errors are transient and retryable, but corrupt config is a fatal condition that callers need to know about.

## configFileExists checks the wrong key

`configFileExists()` always checks the global `file_key` (`vault_access.json`), not the `file_name` parameter passed to `loadVaultConfiguration`. This is a known limitation. If `loadVaultConfiguration` is called with a different filename, the existence check may give a wrong answer.

## Never swallow S3 exceptions in backup discovery

The original bug was: `getLatestBackupfromS3()` caught all S3 exceptions and returned `None`, which `main.py` interpreted as "no backup exists" and triggered a fresh vault init — destroying existing data. All S3 exceptions in backup discovery must re-raise.

## Never log vault secrets

Vault config files contain unseal keys and root tokens. Error messages in `loadVaultConfiguration` intentionally omit the exception detail (`{e}`) to avoid leaking JSON fragments that could contain secrets.

## ENABLE_RESTORE is case-insensitive

Normalized with `.lower()` at startup. All comparisons use `== "true"`. If adding new env var checks, follow the same pattern.

## CAPTAIN_DOMAIN must be set when restore is enabled

Validated at startup in `main.py`. If missing, `sys.exit(1)`. Without this, S3 prefix construction produces `None/hashicorp-vault-backups/...` which silently queries the wrong path.
