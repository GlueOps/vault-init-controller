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
    vault_sts_name = os.getenv("VAULT_STS_NAME", "vault")
    vault_k8s_service_name = os.getenv("VAULT_K8S_SERVICE_NAME", "vault-internal")
    service_port = os.getenv("SERVICE_PORT", "8200")
    vault_label_selector = os.getenv("VAULT_LABEL","app.kubernetes.io/name=vault")
    reconcile_period = int(os.getenv("RECONCILE_PERIOD", "10"))

    vaultClient = vault_k8s_utils.VaultManager(namespace,vault_sts_name,vault_k8s_service_name,service_port,vault_label_selector)
    # Start the control loop to watch the vault pods
    while(True):
        logger.info("Reconciling on vault server...")
        vault_pods = vaultClient.get_vault_pods()
        if(len(vault_pods) == 0):
            logger.info("No vault pods found with the label "+vault_label_selector+" in "+namespace)
            time.sleep(reconcile_period)
            continue
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
                if(vaultClient.isVaultSealed("https://"+vault_sts_name+"-"+str(i)+"."+vault_k8s_service_name+"."+namespace+":"+service_port+vault_status_url_path)):
                   vaultClient.vaultUnseal("https://"+vault_sts_name+"-"+str(i)+"."+vault_k8s_service_name+"."+namespace+":"+service_port+vault_unseal_url_path)
                else:
                   logger.info(vault_sts_name+"-"+str(i)+" is already unsealed")
    
        if(vaultClient.vaultHealthCheck() != None):
            logger.info("Vault cluster is up and running")
        time.sleep(reconcile_period)
