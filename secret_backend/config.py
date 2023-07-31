import os
import json

homeDir = os.path.expanduser("~")
configFile = os.path.join(homeDir, ".vault-config.json")

def configFileExists():
  return os.path.exists(configFile)

def loadVaultConfiguration():
  with open(configFile, "r") as data:
    return json.load(data)

def saveVaultConfiguration(content):
  file = open(configFile, "w")
  file.write(content)
  file.close()