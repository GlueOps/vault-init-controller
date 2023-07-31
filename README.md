## Vault init controller

#### A controller that watches for vault pods and unseals the vault server 

## Configuration

The GlueOps vault init controller project utilizes environment variables to configure its behavior. The following table outlines the environment variables and their default values if not explicitly set:

| Environment Variable       | Description                                       | Default Value       |
|--------------------------- |---------------------------------------------------|---------------------|
| `NAMESPACE`                | Kubernetes namespace in which Vault is deployed.  | `glueops-core-vault`|
| `VAULT_K8S_SERVICE_NAME`   | The name of the Kubernetes service for Vault.     | `vault-internal`    |
| `RECONCILE_PERIOD`         | Interval (in minutes) for secret reconciliation.  | `5`                 |
| `SERVICE_PORT`             | Port number on which Vault service is exposed.    | `8200`              |


## Usage

To utilize vault init controller project, ensure you have the necessary environment variables set according to your desired configuration. These variables will be read by the application to determine its behavior.

### Example

```bash
# Set the environment variables before running the GlueOps Core Vault application
export NAMESPACE="my-vault-namespace"
export VAULT_K8S_SERVICE_NAME="my-vault-service"
export RECONCILE_PERIOD=10
export SERVICE_PORT="8300"