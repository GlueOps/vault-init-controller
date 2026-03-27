import json
import logging
import os
import re
import boto3
from datetime import datetime, timedelta


class BackupNotFoundError(Exception):
    pass


#init child logger
logger = logging.getLogger('VAULT_INIT.config')

SNAP_KEY_PATTERN = re.compile(
    r".+/(\d{4}-\d{2}-\d{2})/vault_(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.snap$"
)


def _validate_snap_key(key):
    match = SNAP_KEY_PATTERN.match(key)
    if not match:
        return False
    dir_date_str, file_date_str = match.group(1), match.group(2)
    try:
        dir_date = datetime.strptime(dir_date_str, "%Y-%m-%d")
        file_date = datetime.strptime(file_date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return False
    if dir_date.date() != file_date.date():
        return False
    if dir_date.strftime("%Y-%m-%d") != dir_date_str:
        return False
    if file_date.strftime("%Y-%m-%dT%H:%M:%S") != file_date_str:
        return False
    return True


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
    if not configFileExists():
        return None
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        json_data = obj['Body'].read().decode('utf-8')
    except Exception as e:
        logger.error(f"Error loading vault configuration: {str(e)}")
        return None
    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        logger.error("Vault configuration file contains invalid JSON")
        raise ValueError("Vault configuration file contains invalid JSON")

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

        if restore_this_backup:
            return _findSpecificBackup(paginator)
        else:
            return _findLatestBackup(paginator)
    except BackupNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error checking backup in s3: {str(e)}")
        raise


def _findSpecificBackup(paginator):
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=captain_domain + "/" + backup_prefix)
    for page in page_iterator:
        if "Contents" in page:
            for obj in page['Contents']:
                if not obj['Key'].endswith('.snap'):
                    continue
                if os.path.basename(obj['Key']) == restore_this_backup:
                    if not _validate_snap_key(obj['Key']):
                        raise ValueError(f"Backup key does not match expected date format: {obj['Key']}")
                    logger.info(f"Restoring this backup: {restore_this_backup}")
                    return obj
    raise BackupNotFoundError(f"RESTORE_THIS_BACKUP is set to '{restore_this_backup}' but no matching backup was found in S3")


def _findLatestBackup(paginator):
    today = datetime.utcnow().date()
    for days_ago in range(45):
        target_date = today - timedelta(days=days_ago)
        date_prefix = f"{captain_domain}/{backup_prefix}/{target_date.isoformat()}/"
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=date_prefix)
        latest_snap = None
        for page in page_iterator:
            if "Contents" in page:
                for obj in page['Contents']:
                    if not obj['Key'].endswith('.snap'):
                        continue
                    if not _validate_snap_key(obj['Key']):
                        raise ValueError(f"Backup key does not match expected date format: {obj['Key']}")
                    latest_snap = obj
        if latest_snap:
            logger.info(f"Latest backup found: {latest_snap['Key']}")
            return latest_snap

    logger.info("No .snap backups found in S3")
    return None
