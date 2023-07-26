from kubernetes import client, config
import subprocess
import os
import re
from utils.logging_config import logger

def get_vault_pods(namespace):
    try:
        # Load the default Kubernetes configuration
        config.load_kube_config()

        # Create a Kubernetes API client
        v1 = client.CoreV1Api()

        # Get vault pods in the cluster in the vault namespace
        pods = v1.list_namespaced_pod(namespace)
        return pods.items

    except Exception as e:
        logger.error(f"Error: {e}")
        return []

def get_vault_status():
    output = subprocess.run(["kubectl", "exec", "-i", "vault-0", "-n", "glueops-core-vault", "--", "vault", "status"],stdout = subprocess.PIPE)
   
    # Initialize an empty dictionary to store the parsed data
    parsed_data = {}

    # Split the output into lines
    lines = output.stdout.splitlines()

    # Remove the header line (first line) from the lines list
    lines.pop(0)
    lines.pop(0)

    # Use regular expression to find key-value pairs and add them to the dictionary
    for line in lines:
        match = re.match(r"\s*(\S.*?)\s{2,}(.*)", str(line,'UTF8'))
        if match:
            key, value = match.groups()
            parsed_data[key] = value.strip()

    return parsed_data

def init_vault(terraform_dir):
    logger.info(" Starting to Initialize Vault....")
    
    # check if terraform init happened and skip to terraform plan
    if os.path.exists(terraform_dir) and os.path.isdir(terraform_dir):
        logger.info("terraform was already initialized...Moving to terraform plan.")
        subprocess.run(["terraform", "plan"])
    else:
        subprocess.run(["terraform", "init"])
        subprocess.run(["terraform", "plan"])
    
    # set env variable to skip tls verify for vault server 
    os.environ['VAULT_SKIP_VERIFY'] = "true"

    # vault init and unseal via terraform apply
    subprocess.run(["terraform", "apply","--auto-approve"])
