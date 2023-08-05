import time
import vault_k8s_utils.utils as vault_k8s_utils
from utils.logging_config import logger
import warnings
import os

 # To ignore https warnings
warnings.filterwarnings("ignore")


vault_status_url_path  = '/v1/sys/health'
vault_unseal_url_path  = '/v1/sys/unseal'

if __name__ == "__main__":

    # Read values from environment variables if available, otherwise use default values
    namespace = os.getenv("NAMESPACE", "glueops-core-vault")
    vault_k8s_service_name = os.getenv("VAULT_K8S_SERVICE_NAME", "vault-internal")
    sts_name = os.getenv("VAULT_STS_NAME", "vault")
    reconcile_period = int(os.getenv("RECONCILE_PERIOD", "5"))
    service_port = os.getenv("SERVICE_PORT", "8200")
    leader_vault_instance = sts_name+"-0"

    vaultClient = vault_k8s_utils.VaultManager(namespace,vault_k8s_service_name,service_port,leader_vault_instance)
    # Start the control loop to watch the vault pods
    while(True):
        vault_pods = vaultClient.get_vault_pods()
        all_pods_running = True
        for pod in vault_pods:
            if(pod.status.phase == "Running"):
                continue
            else:
                all_pods_running = False
                break
        if(all_pods_running == False):
            logger.info("Not all vault pods are up and running....Retrying after 5 seconds")
            time.sleep(reconcile_period)
            continue
        else: 
            logger.info("All vaults pods are up and running")
            # check vault status 
            if(not vaultClient.isVaultIntialized()):
                vaultClient.initializeVault()
                
            else:
               logger.info('Vault is already Initialized')
            for i in range(0,len(vault_pods)):
               #check if each vault server in the cluster is unsealed
                if(vaultClient.isVaultSealed("https://"+sts_name+"-"+str(i)+"."+vault_k8s_service_name+"."+namespace+":"+service_port+vault_status_url_path)):
                   vaultClient.vaultUnseal("https://"+sts_name+"-"+str(i)+"."+vault_k8s_service_name+"."+namespace+":"+service_port+vault_unseal_url_path)
                else:
                   logger.info("vault-"+str(i)+" is already unsealed")
                 # TODO: Add vault health check 
        time.sleep(reconcile_period)
