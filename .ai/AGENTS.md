# AI Agent Guide for vault-init-controller

A Kubernetes controller that watches for Vault pods and manages initialization, unsealing, and backup restoration. Runs as a `while True` reconcile loop in a container.

```
main.py                      # Reconcile loop, env var config, orchestration
secret_backend/config.py     # S3 operations, backup discovery, key validation
vault_k8s_utils/utils.py     # Kubernetes + Vault HTTP API interactions
```

## Detailed guides

- [Architecture & Design Decisions](architecture.md)
- [Testing Patterns](testing.md)
- [Common Pitfalls](pitfalls.md)

## Environment variables

See `README.md` for the full list. Key ones for AI context:
- `ENABLE_RESTORE` — set to `"true"` to restore from backup (case-insensitive, normalized with `.lower()`)
- `CAPTAIN_DOMAIN` — required when restore is enabled, validated at startup
- `RESTORE_THIS_BACKUP` — optional, set to a specific `.snap` filename to restore that exact backup

## Code style

- No type annotations in existing code
- Logging via `logging.getLogger('VAULT_INIT.config')` / `'VAULT_INIT.utils'`
- Errors that risk data loss should log at `error` level
- Never log vault secrets (keys, tokens, JSON config contents)
