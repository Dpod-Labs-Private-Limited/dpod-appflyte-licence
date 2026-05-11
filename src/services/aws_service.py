import os
import boto3
from dotenv import load_dotenv
from datetime import datetime
from botocore.exceptions import ClientError

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_REGION = os.getenv("AWS_REGION", None)

_secrets_client = boto3.client(
    'secretsmanager',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

_dynamodb_resource = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

_licenses_table = _dynamodb_resource.Table("appflyte_licenses")


class AwsSecretService:

    def get_aws_secret(secret_name):

        # Force secret name and secret value to be strings
        secret_name = str(secret_name)

        # Create the secret
        response = _secrets_client.get_secret_value(SecretId=secret_name)

        return response['SecretString']

    def if_secret_name_exists(secret_name):

        try:
            # Attempt to describe the secret
            _secrets_client.describe_secret(SecretId=secret_name)
            print(f"The secret '{secret_name}' exists.")
            return True

        except _secrets_client.exceptions.ResourceNotFoundException:
            print(f"The secret '{secret_name}' does not exist.")
            return False

    def create_aws_secret(secret_name, secret_value):

        try:
            # Force secret name and secret value to be strings
            secret_name = str(secret_name)
            secret_value = str(secret_value)

            # Create the secret
            _secrets_client.create_secret(Name=secret_name, SecretString=secret_value)

        except Exception as e:
            print(e)

def store_license(subscription_id, license_token, license_public_key,  root_username, root_password):
    try:

        _licenses_table.put_item(
            Item = {
                "subscription_id": subscription_id,
                "license_token": license_token,
                "license_public_key": license_public_key,
                "root_username": root_username,
                "root_password": root_password,
                "created_at": datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_not_exists(subscription_id)"
        )
        print("Inserted successfully")

    except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print("❌ License already exists for this subscription")
            else:
                raise
