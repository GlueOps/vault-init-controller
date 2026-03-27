# Architecture & Design Decisions

## Backup discovery uses S3 lexicographic key ordering

Backup keys follow `{CAPTAIN_DOMAIN}/{BACKUP_PREFIX}/{YYYY-MM-DD}/vault_{YYYY-MM-DDThh:mm:ss}.snap`. S3 `list_objects_v2` returns keys in ascending lexicographic order. Since ISO 8601 timestamps with zero-padding sort lexicographically in chronological order, the last `.snap` key is always the latest backup. This eliminates per-object `get_object_tagging` API calls.

## Day-by-day reverse search

`_findLatestBackup` searches from today backward (up to 45 days) using date-scoped S3 prefixes (e.g. `{domain}/{prefix}/2026-03-16/`). This avoids listing the entire backup history. In the common case (backups exist today), it's a single S3 API call.

## Key format validation is safety-critical

`_validate_snap_key()` ensures keys are zero-padded ISO 8601 so lexicographic ordering equals chronological ordering. It uses:
1. Regex for structural format (fixed-width digits, correct separators)
2. `datetime.strptime` to catch impossible dates (month 13, Feb 30, etc.)
3. Directory date must match file date
4. `strftime` round-trip check as defense against `strptime` leniency

If validation fails, the controller raises immediately rather than silently restoring a wrong backup.

## S3 errors must never trigger a fresh vault init

Exceptions from S3 calls are re-raised and caught in `main.py`, which skips the init cycle. This prevents data loss from transient S3 issues being misinterpreted as "no backup exists." This was the original bug that prompted these safety improvements.

## BackupNotFoundError

A custom exception for when `RESTORE_THIS_BACKUP` is set but no matching key is found. This crashes the controller via `sys.exit(1)` to make misconfiguration visible (Kubernetes CrashLoopBackOff). It is explicitly not caught by the generic `except Exception` retry handler.

## Two backup discovery paths

`getLatestBackupfromS3()` dispatches to:
- `_findLatestBackup(paginator)` — date-scoped reverse search, validates all keys, returns latest
- `_findSpecificBackup(paginator)` — full listing, validates only the matched key, stops on match
