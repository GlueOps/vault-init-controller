import logging

from kubernetes import (
  client as k8s_client,
  config as k8s_config
)
import requests
from secret_backend import config as secret_config


#init child logger
logger = logging.getLogger('VAULT_INIT.utils')

class VaultManager:

  def __init__(self,vault_namespace,vault_sts_name,vault_k8s_service_name,service_port,vault_label_selector):
      self.vault_namespace = vault_namespace
      self.vault_k8s_service_name = vault_k8s_service_name
      self.service_port = service_port
      self.vault_sts_name = vault_sts_name
      self.vault_label_selector = vault_label_selector
      self.vault_init_url_path = '/v1/sys/init'

      # setting cluster config
      try:
          k8s_config.load_incluster_config()
          logger.info("Loaded incluster kubeconfig")
      except Exception as e:
          logger.warning(f'Error loading in-cluster k8s config: {e}')
          try:
              logger.info('Using local Kubeconfig (not in-cluster)')
              k8s_config.load_kube_config()
          except Exception:
              logger.exception('Failed to load Kubeconfig from cluster, local file')
  
  def get_vault_pods(self):
      try:
          # Create a Kubernetes API client
          v1 = k8s_client.CoreV1Api()

          # Get vault pods in the cluster in the vault namespace
          pods = v1.list_namespaced_pod(self.vault_namespace,label_selector=self.vault_label_selector)
          return pods.items

      except Exception as e:
          logger.error(f"Error: {e}")
          return []

  def isVaultIntialized(self):
      vault_init_url = "https://"+self.vault_sts_name+"-0"+"."+self.vault_k8s_service_name+"."+self.vault_namespace+":"+self.service_port+self.vault_init_url_path
      response = requests.get(vault_init_url,verify=False)
      return response.json()['initialized']

  def isVaultSealed(self,vault_url):
    status = self.vaultGetSealStatus(vault_url)
    return status['sealed']

  def initializeVault(self,shares=1, threshold=1, secret_file_name="vault_access.json"):
    logger.info("Starting to initialize vault...")
    payload = '{"secret_shares" : %d, "secret_threshold" : %d}' % (shares, threshold)
    vault_init_url = "https://"+self.vault_sts_name+"-0"+"."+self.vault_k8s_service_name+"."+self.vault_namespace+":"+self.service_port+self.vault_init_url_path
    if(secret_config.bucketExists):
      try:
        r = requests.put(vault_init_url, data=payload,verify=False)
        secret_config.saveVaultConfiguration(r.text, secret_file_name)
        return r.json()
      except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        logger.error("ERR: Error connecting to Vault server")
        exit()
    else:
       exit()

  def vaultGetSealStatus(self,vault_url):
    try:
      r = requests.get(vault_url,verify=False)
      return r.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
      logger.error("ERR: Error connecting to Vault server ")
      exit()

  def vaultUnseal(self,vault_url,vault_key_threshold,secret_file):
      if not secret_config.configFileExists():
          logger.error("ERR: Vault config file not found")
          exit()

      config = secret_config.loadVaultConfiguration(secret_file)
      keys = config['keys']

      threshold = vault_key_threshold
      progress = 0

      for i in range(progress, threshold):
          payload = '{"key" : "%s"}' % (keys[i])
          try:
              r = requests.put(vault_url, data=payload,verify=False)
              # logger.info(r.text)
              # if(r.status_code == 400):
              #    logger.error("Unsealing with wrong keys")
          except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
              logger.error("ERR: Error connecting to Vault server")

  def vaultHealthCheck(self):
    try:
        response = requests.get("https://"+self.vault_k8s_service_name+"."+self.vault_namespace+":"+self.service_port+"/v1/sys/health",verify=False)
        response_data = response.json()
        
        # Check the status code to ensure the request was successful
        if response.status_code == 200:
            # Process the response data as needed
            return response_data
        else:
            logger.info("Vault health status. Status code: "+str(response.status_code))
            return None

    except requests.exceptions.RequestException as e:
        logger.error("Error occurred:", e)
        return None

  def restoreVaultfromS3(self, latest_backup):
    try:
        logger.info("Downloading vault backup from s3...")
        response = secret_config.s3.get_object(Bucket=secret_config.bucket_name, Key=latest_backup)
        logger.info("Backup content lenght: "+str(response['ContentLength']))
        temp_file_name = secret_config.file_key.replace("vault_access.json","vault_access_temp.json")
        data = secret_config.loadVaultConfiguration(temp_file_name)
        vault_token = data['root_token']
        headers = {
            'X-Vault-Token': vault_token
        }
        restore_url = "https://"+self.vault_sts_name+"-0"+"."+self.vault_k8s_service_name+"."+self.vault_namespace+":"+self.service_port+"/v1/sys/storage/raft/snapshot-force"
        logger.info("Restoring vault backup "+latest_backup)
        res = requests.put(restore_url, headers=headers, data=response['Body'], verify=False)
        logger.info(res.text)
        if res.status_code == 204:
          logger.info("Existing backup was restored successfully")
    except Exception as e:
        logger.error("Error occurred:", e)
