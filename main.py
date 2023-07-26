import os 
import time
import vault_k8s_utils.utils as vault_k8s_utils
from utils.logging_config import logger


if __name__ == "__main__":
    
    namespace = "glueops-core-vault"
    retry_threshold = 5
    retry_count = 0     # TODO: Use retry_threshold if necessary

    current_dir = os.getcwd()
    terraform_dir = os.path.join(current_dir,'terraform/vault-init','.terraform')
    os.chdir(current_dir+"/terraform/vault-init")

    # Start the control loop to watch the vault pods
    while(True):
        vault_pods = vault_k8s_utils.get_vault_pods(namespace)
        all_pods_running = True
        for pod in vault_pods:
            if(pod.status.phase == "Running"):
                continue
            else:
                all_pods_running = False
                break
        if(all_pods_running == False):
            logger.info("Not all vault pods are up and running....Retrying after 5 seconds")
            time.sleep(5)
            continue
        else: 
            logger.info("All vaults pods are up and running")
            # check if vault is unsealed or not
            vault_status = vault_k8s_utils.get_vault_status()
            if(vault_status['Sealed'] == 'false' and vault_status['Initialized'] == 'true'):
                logger.info('Vault is already unsealed and ready to use')
            else:
                vault_k8s_utils.init_vault(terraform_dir)