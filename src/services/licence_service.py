import jwt
import json
import logging
import datetime

from src.utils.models_utils import LicenceRequest
from src.services.aws_service import AwsSecretService
from src.services.utility_service import UtilityService
from src.services.password_service import LicencePasswordService

logger = logging.getLogger(__name__)

def get_curr_datetime_str() -> str:
    dt = datetime.datetime.utcnow()
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt_str

def generate_key_pair(subscriber_id:str):
    
    # Generate key pair
    generated_key_pair = UtilityService.generate_key_pair()
    
    stage = UtilityService.get_stage()
    secret_name = 'App-Flyte/Key-Pair/{}/{}'.format(stage, subscriber_id)
    
    # Check if secret name exists
    if not AwsSecretService.if_secret_name_exists(secret_name=secret_name):
        AwsSecretService.create_aws_secret(secret_name=secret_name, secret_value=json.dumps(generated_key_pair))
        
    # Fetch key pair from the AWS secrets manager
    fetched_secret = AwsSecretService.get_aws_secret(secret_name)
    return json.dumps(fetched_secret)

def generate_licence(data:LicenceRequest, body:dict):
    
    subscriber_id = data.subscriber_id
    subscription_id = data.subscription_id
    account_id = data.account_id
    root_user_id = data.root_user_id
    root_username = data.root_username
    
    service_type = data.service_type
    aws_database_details = None
    azure_database_details = None
    aws_service_details = None
    azure_service_details = None

    # Generate key pair
    response = generate_key_pair(subscriber_id)

    while isinstance(response, str):
        response = json.loads(response)

    public_key = response['public_key']
    private_key = response['private_key']
    
    trialStartDate = datetime.datetime.today().date()
    trialEndDate = trialStartDate + datetime.timedelta(days=365)
    trialStartDateStr = trialStartDate.isoformat()
    trialEndDateStr = trialEndDate.isoformat() 
    random_generated_password = LicencePasswordService.generate_password(8)
    hashed_password = LicencePasswordService.hash_password(random_generated_password)
    hash_secret = UtilityService.generate_salt(public_key, account_id)

    if service_type == 'aws':
        aws_database_details = body["database_details"]
        aws_service_details = body["service_details"]
    else:
        azure_database_details = body["database_details"]
        azure_service_details = body["service_details"]

    jwt_token_payload = {
        "root_account_id": account_id,
        "root_user_id": root_user_id,
        "root_username": root_username,
        "password": hashed_password,
        "subscriber_id": subscriber_id,
        "subscription_id": subscription_id,
        "subscription_start_date": trialStartDateStr,
        "subscription_end_date": trialEndDateStr,
        "app_subscribed": ["appflyte-frontend", "appflyte-backend", "Impilos", "ISSAC", "Ameya"],
        "database": body["database"],
        "hash_secret": hash_secret,
        "dynamo": aws_database_details,
        "cosmos": azure_database_details,
        "aws": aws_service_details,
        "azure": azure_service_details
    }
    
    jwt_token = UtilityService.create_jwt(payload=jwt_token_payload, private_key=private_key, exp_date=trialEndDate)
    return jwt_token, public_key, random_generated_password

def get_licence(data:LicenceRequest):
    
    subscription_id = data.subscription_id
    service_type = data.service_type
    aws_access_key_id = data.aws_access_key_id
    aws_secret_access_key = data.aws_secret_access_key
    aws_region_name = data.region_name
    
    req_body = {
        "database": None,
        "service_details": None,
        "database_details": None
    }

    if service_type == 'aws':
            
        req_body['database'] = "dynamo"
        
        req_body['service_details'] = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "region_name": aws_region_name
        }
        
        req_body['database_details'] = {
            "access_key": aws_access_key_id,
            "table_name": f"applyte-table-{subscription_id}"
        }

    else:
        pass
    
    jwt_token, public_key, generated_password = generate_licence(data, req_body)    
    public_key = public_key.encode('utf-8')
    
    dpod_license = {
        "jwt_token": jwt_token,
        "public_key": UtilityService.base64_url_encode(public_key),
        "root_password": generated_password
    }
    
    return dpod_license

def generate_root_user_token(jwt_token, public_key, algorithm = 'HS256'):
                
    try:
        decoded_payload = jwt.decode(jwt_token, public_key, algorithms=[algorithm], options={"verify_signature": False}, verify=False)
    except Exception as e:
        raise ValueError('License key not correctly formatted')
    
    subscriber_id = decoded_payload['subscriber_id']
    subscription_id = decoded_payload['subscription_id']
    password = decoded_payload['password']
    root_username = decoded_payload['root_username']
    trial_end_date = decoded_payload['subscription_end_date']

    key = root_username + subscriber_id + subscription_id
    encrypted_userinfo = UtilityService.generate_salt(key, password)
    
    # Expiration of the token should be 24 hr from generation
    curr_time = datetime.datetime.utcnow()
    exp_time = curr_time + datetime.timedelta(hours=24)
    exp_timestamp = int(exp_time.timestamp())

    # For temporary : Expiration of the token should be same as license expiration
    exp_datetime = datetime.datetime.strptime(trial_end_date, "%Y-%m-%d")
    exp_timestamp = int(exp_datetime.timestamp())

    # Rootusertoken is a JWT signed using algorith HS256 and shared private key as license public key
    payload = {
        'sub': encrypted_userinfo,
        'exp': exp_timestamp
    }

    signed_jwt = jwt.encode(payload=payload, algorithm='HS256', key=jwt_token)
    return signed_jwt
