import os
import time
import warnings

from glueops.setup_logging import configure as go_configure_logging

import vault_k8s_utils.utils as vault_k8s_utils
import secret_backend.config as secret_config

# configure logger
logger = go_configure_logging(
    name='VAULT_INIT',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

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
    pause_reconcile = os.getenv("PAUSE_RECONCILE","false")
    vault_key_shares = int(os.getenv("VAULT_KEY_SHARES","1"))
    vault_key_threshold = int(os.getenv("VAULT_KEY_THRESHOLD","1"))
    file_key = os.getenv("VAULT_SECRET_FILE", "vault_access.json")
    restore_enabled = os.getenv("ENABLE_RESTORE","false")

    vaultClient = vault_k8s_utils.VaultManager(namespace,vault_sts_name,vault_k8s_service_name,service_port,vault_label_selector)

    # Start the control loop to watch the vault pods
    while(True):

        # Pause reconciling if PAUSE_RECONCILE is true 
        if(pause_reconcile == "true"):
            logger.info("Reconciling have been paused on vault servers...")
            time.sleep(reconcile_period)
            continue

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
            backup_found = False
            backup_restored = False
            # check vault status 
            if(not vaultClient.isVaultIntialized()):
                # Check if a backup already exists, if yes restore
                latest_backup = secret_config.getLatestBackupfromS3()
                config_file_exist = secret_config.configFileExists()
                if restore_enabled=="true" and latest_backup and config_file_exist:
                    backup_found = True
                    logger.info("Backup found, intializing vault...")
                    temp_file_name = secret_config.file_key.replace("vault_access.json","vault_access_temp.json")
                    vaultClient.initializeVault(vault_key_shares,vault_key_threshold,temp_file_name)
                else:
                    logger.info("Backup or keys doesn't exist, initializing vault from scratch..")
                    vaultClient.initializeVault(vault_key_shares,vault_key_threshold,file_key)   

            else:
               logger.info('Vault is already Initialized')
            
            secret_file  = file_key
            if restore_enabled=="true" and backup_found and not backup_restored:
                secret_file = file_key.replace("vault_access.json","vault_access_temp.json")
                
            for i in range(0,len(vault_pods)):
               #check if each vault server in the cluster is unsealed
                if(vaultClient.isVaultSealed("https://"+vault_sts_name+"-"+str(i)+"."+vault_k8s_service_name+"."+namespace+":"+service_port+vault_status_url_path)):
                   vaultClient.vaultUnseal("https://"+vault_sts_name+"-"+str(i)+"."+vault_k8s_service_name+"."+namespace+":"+service_port+vault_unseal_url_path,vault_key_threshold,secret_file)
                else:
                   logger.info(vault_sts_name+"-"+str(i)+" is already unsealed")

            if restore_enabled=="true" and backup_found and not backup_restored:
                vaultClient.restoreVaultfromS3(latest_backup['Key'])
                backup_restored = True
    
        if(vaultClient.vaultHealthCheck() != None):
            logger.info("Vault cluster is up and running")
        time.sleep(reconcile_period)
