## Vault init controller

#### A controller that watches for vault pods and unseals the vault server 

## Configuration

The GlueOps vault init controller project utilizes environment variables to configure its behavior. The following table outlines the environment variables and their default values if not explicitly set:

| Environment Variable       | Description                                       | Default Value                 |
|--------------------------- |---------------------------------------------------|-------------------------------|
| `NAMESPACE`                | Kubernetes namespace in which Vault is deployed.  | `glueops-core-vault`          |
| `VAULT_STS_NAME        `   | The name of the Kubernetes statefulset for Vault. | `vault`                       |
| `VAULT_LABEL_SELECTOR  `   | The label selector for the vault pods .           | `app.kubernetes.io/name=vault`|
| `VAULT_K8S_SERVICE_NAME`   | The name of the Kubernetes service for Vault.     | `vault-internal`              |
| `RECONCILE_PERIOD`         | Interval (in minutes) for secret reconciliation.  | `10`                          |
| `SERVICE_PORT`             | Port number on which Vault service is exposed.    | `8200`                        |
| `VAULT_S3_BUCKET`          | The s3 bucket to store the vault unseal keys .    | `vault-backend-glueops`       |
| `VAULT_SECRET_FILE`        | The file path in the s3 bucket.                   | `vault-config.json`           |
| `PAUSE_RECONCILE  `        | To pause the reconcile of the controller.         | `false`                        |   

## Prerequisite

The VM where the applicaiton is running is expected to have the permissions to write to the s3 bucket that is mentioned in `VAULT_S3_BUCKET` env variable above.