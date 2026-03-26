import json
import logging
import os
import boto3


class BackupNotFoundError(Exception):
    pass


#init child logger
logger = logging.getLogger('VAULT_INIT.config')


# Replace this with your bucket name
bucket_name = os.getenv("VAULT_S3_BUCKET", "vault-backend-glueops")
file_key = os.getenv("VAULT_SECRET_FILE", "vault_access.json")
captain_domain = os.getenv("CAPTAIN_DOMAIN")
backup_prefix = os.getenv("BACKUP_PREFIX","hashicorp-vault-backups")
restore_this_backup = os.getenv("RESTORE_THIS_BACKUP")
# Create a global S3 client
s3 = boto3.client('s3')

# Function to check if the configuration file exists in S3
def configFileExists():
    try:
        # Check if the file exists in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=file_key)     
        if 'Contents' in response:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error checking if config file exists: {str(e)}")
        raise

# Function to load the JSON configuration from S3
def loadVaultConfiguration(file_name):
    try:
        # Check if the file exists before proceeding to read
        if configFileExists():
            obj = s3.get_object(Bucket=bucket_name, Key=file_name)
            json_data = obj['Body'].read().decode('utf-8')
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError:
                logger.error("Vault configuration file contains invalid JSON")
                raise ValueError("Vault configuration file contains invalid JSON")

            return data
        else:
            return None    
    except Exception as e:
        logger.error(f"Error loading vault configuration: {str(e)}")
        return None

# Function to save the JSON configuration to S3
def saveVaultConfiguration(json_data, secret_file_name):
    try:
        json_string = json.dumps(json.loads(json_data), indent=2)
        # Save the JSON data to S3
        s3.put_object(Bucket=bucket_name, Key=secret_file_name, Body=json_string, ContentType='application/json')  
    except Exception as e:
        logger.error(f"Error saving vault configuration: {str(e)}")
        raise

# Check if the bucket exists
def bucketExists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        # Catch the exception if the bucket doesn't exist
        if '404' in str(e):
            return False
        else:
            logger.error(f"Error checking if the bucket exists: {str(e)}")
            return False

def getLatestBackupfromS3():
    try:
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name,Prefix=captain_domain+"/"+backup_prefix)
        latest_snap = None
        for page in page_iterator:
            if "Contents" in page:
                for obj in page['Contents']:
                    if not obj['Key'].endswith('.snap'):
                        continue
                    if restore_this_backup and os.path.basename(obj['Key']) == restore_this_backup:
                        logger.info(f"Restoring this backup: {restore_this_backup}")
                        return obj
                    latest_snap = obj

        if restore_this_backup:
            raise BackupNotFoundError(f"RESTORE_THIS_BACKUP is set to '{restore_this_backup}' but no matching backup was found in S3")

        if latest_snap:
            logger.info(f"Latest backup found: {latest_snap['Key']}")
        else:
            logger.info("No .snap backups found in S3")

        return latest_snap
    except BackupNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error checking backup in s3: {str(e)}")
        raise
