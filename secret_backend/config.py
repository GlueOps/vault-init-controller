import boto3
import json 
from utils.logging_config import logger

# Replace this with your bucket name
bucket_name = 'vault-backend-glueops'
file_key = 'vault-config.json'

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
        logger.info(f"Error checking if config file exists: {str(e)}")
        return False

# Function to load the JSON configuration from S3
def loadVaultConfiguration():
    try:
        # Check if the file exists before proceeding to read
        if configFileExists():
            obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            json_data = obj['Body'].read().decode('utf-8')
            #Remove the newline character from the end of the JSON string
            json_string_cleaned = json_data.strip()

            # Split the JSON string by newline characters (if there are multiple JSON objects separated by newlines)
            json_objects = json_string_cleaned.split("\n")

            # Initialize an empty list to store the parsed JSON objects
            parsed_data = []

            # Parse each JSON object separately
            for obj in json_objects:
                try:
                    data = json.loads(obj)
                    parsed_data.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")

            return json.loads(parsed_data[0])
        else:
            return None
        
    except Exception as e:
        logger.info(f"Error loading vault configuration: {str(e)}")
        return None

# Function to save the JSON configuration to S3
def saveVaultConfiguration(json_data):
    try:
        json_string = json.dumps(json_data, indent=2)
        
        # Save the JSON data to S3
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=json_string)
        
    except Exception as e:
        logger.info(f"Error saving vault configuration: {str(e)}")

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
            logger.info(f"Error checking if the bucket exists: {str(e)}")
            return False
