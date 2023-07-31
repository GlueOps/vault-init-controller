from kubernetes import client, config
import requests
from utils.logging_config import logger
import secret_backend 

# setting cluster config
try:
    config.load_incluster_config()
    logger.info("Loaded incluster kubeconfig")
except Exception as e:
    logger.warning(f'Error loading in-cluster k8s config: {e}')
    try:
        logger.info('Using local Kubeconfig (not in-cluster)')
        config.load_kube_config()
    except Exception:
        logger.exception('Failed to load Kubeconfig from cluster, local file')

vault_init_url_path = '/v1/sys/init' 

class VaultManager:

  def __init__(self,vault_namespace,vault_k8s_service_name,service_port):
     self.vault_namespace = vault_namespace
     self.vault_k8s_service_name = vault_k8s_service_name
     self.service_port = service_port

  def get_vault_pods(self):
      try:
          # Create a Kubernetes API client
          v1 = client.CoreV1Api()

          # Get vault pods in the cluster in the vault namespace
          pods = v1.list_namespaced_pod(self.vault_namespace)
          return pods.items

      except Exception as e:
          logger.error(f"Error: {e}")
          return []

  def isVaultIntialized(self):
      vault_init_url = "https://"+self.vault_k8s_service_name+"."+self.vault_namespace+":"+self.service_port+vault_init_url_path
      response = requests.get(vault_init_url,verify=False)
      return response.json()['initialized']

  def isVaultSealed(self,vault_url):
    status = self.vaultGetSealStatus(vault_url)
    return status['sealed']

  def initializeVault(self,shares=5, threshold=3):
    payload = '{"secret_shares" : %d, "secret_threshold" : %d}' % (shares, threshold)
    vault_init_url = "https://"+self.vault_k8s_service_name+"."+self.vault_namespace+":"+self.service_port+vault_init_url_path
    try:
      r = requests.put(vault_init_url, data=payload,verify=False)
      secret_backend.saveVaultConfiguration(r.text)
      return r.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
      logger.error("ERR: Error connecting to Vault server")
      exit()

  def vaultGetSealStatus(self,vault_url):
    try:
      r = requests.get(vault_url,verify=False)
      return r.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
      logger.error("ERR: Error connecting to Vault server ")
      exit()

  def vaultUnseal(self,vault_url):
      if not secret_backend.configFileExists():
          logger.error("ERR: Vault config file not found")
          exit()

      config = secret_backend.loadVaultConfiguration()
      keys = config['keys']

      threshold = 3
      progress = 0

      for i in range(progress, threshold):
          payload = '{"key" : "%s"}' % (keys[i])
          try:
              r = requests.put(vault_url, data=payload,verify=False)
          except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
              logger.error("ERR: Error connecting to Vault server")
