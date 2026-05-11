
import os
import jwt
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

from src.services.licence_service import get_licence, generate_root_user_token
from src.services.aws_service import store_license
from src.utils.creds_utils import get_licence_creds
from src.utils.models_utils import (
    LicenceRequest,
    ServiceType,
    AwsGenerateLicenceRequest,
    AzureGenerateLicenceRequest,
    AwsRenewLicenceRequest,
    AzureRenewLicenceRequest,
)

load_dotenv()
API_KEY = os.getenv("API_KEY", "my-secret-key")
API_KEY_NAME = "x-api-key"

logger = logging.getLogger(__name__)
app = FastAPI(docs_url="/", redoc_url=None)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid or missing API Key")

def handler(data: LicenceRequest):

    licence_details = get_licence(data)
    jwt_token = licence_details["jwt_token"]
    public_key = licence_details["public_key"]
    root_password = licence_details["root_password"]
    root_user_token = generate_root_user_token(jwt_token, public_key)
    subscription_id = data.subscription_id

    new_licence = {
        "LICENSE_TOKEN": jwt_token,
        "LICENSE_PUBLIC_KEY": public_key,
        "ROOT_USER_TOKEN": root_user_token,
        "ROOT_USER_NAME": data.root_username,
        "ROOT_PASSWORD": root_password,
    }

    store_license(subscription_id, jwt_token, public_key, data.root_username, root_password)

    logger.info("Licence generated successfully...!")
    return new_licence


@app.post("/license/generate/aws", summary="Generate Licence (AWS)")
def generate_licence_aws(req: AwsGenerateLicenceRequest, api_key: str = Depends(verify_api_key)):
    try:
        account_details = get_licence_creds()
        return handler(LicenceRequest(
            account_id=account_details["account_id"],
            subscriber_id=account_details["subscriber_id"],
            subscription_id=account_details["subscription_id"],
            service_type=ServiceType.AWS.value,
            root_user_id=account_details["user_id"],
            root_username=req.mail_id,
            aws_access_key_id=req.aws_access_key_id,
            aws_secret_access_key=req.aws_secret_access_key,
            region_name=req.region_name,
            s3_access_key_id=req.s3_access_key_id,
            s3_secret_access_key=req.s3_secret_access_key,
            s3_region_name=req.s3_region_name,
        ))
    except Exception as e:
        print(f"Error Generating Licence: {e}")
        raise HTTPException(status_code=404, detail="Unable to generate licence")


@app.post("/license/generate/azure", summary="Generate Licence (Azure)")
def generate_licence_azure(req: AzureGenerateLicenceRequest, api_key: str = Depends(verify_api_key)):
    try:
        account_details = get_licence_creds()
        return handler(LicenceRequest(
            account_id=account_details["account_id"],
            subscriber_id=account_details["subscriber_id"],
            subscription_id=account_details["subscription_id"],
            service_type=ServiceType.AZURE.value,
            root_user_id=account_details["user_id"],
            root_username=req.mail_id,
            azure_access_key_id=req.azure_access_key_id,
            s3_access_key_id=req.s3_access_key_id,
            s3_secret_access_key=req.s3_secret_access_key,
            s3_region_name=req.s3_region_name,
        ))
    except Exception as e:
        print(f"Error Generating Licence: {e}")
        raise HTTPException(status_code=404, detail="Unable to generate licence")


def _decode_licence(req):
    try:
        return jwt.decode(
            req.licence_token,
            req.public_key,
            algorithms=['HS256'],
            options={"verify_signature": False},
            verify=False,
        )
    except Exception:
        raise ValueError('License key not correctly formatted')


@app.post("/license/renew/aws", summary="Renew Licence (AWS)")
def renew_licence_aws(req: AwsRenewLicenceRequest, api_key: str = Depends(verify_api_key)):
    try:
        decoded_payload = _decode_licence(req)
        return handler(LicenceRequest(
            account_id=decoded_payload['root_account_id'],
            subscriber_id=decoded_payload['subscriber_id'],
            subscription_id=decoded_payload['subscription_id'],
            service_type=ServiceType.AWS.value,
            root_user_id=decoded_payload['root_user_id'],
            root_username=decoded_payload['root_username'],
            aws_access_key_id=req.aws_access_key_id,
            aws_secret_access_key=req.aws_secret_access_key,
            region_name=req.region_name,
            s3_access_key_id=req.s3_access_key_id,
            s3_secret_access_key=req.s3_secret_access_key,
            s3_region_name=req.s3_region_name,
        ))
    except Exception as e:
        print(f"Error Renewing Licence: {e}")
        raise HTTPException(status_code=404, detail="Unable to renew licence")


@app.post("/license/renew/azure", summary="Renew Licence (Azure)")
def renew_licence_azure(req: AzureRenewLicenceRequest, api_key: str = Depends(verify_api_key)):
    try:
        decoded_payload = _decode_licence(req)
        return handler(LicenceRequest(
            account_id=decoded_payload['root_account_id'],
            subscriber_id=decoded_payload['subscriber_id'],
            subscription_id=decoded_payload['subscription_id'],
            service_type=ServiceType.AZURE.value,
            root_user_id=decoded_payload['root_user_id'],
            root_username=decoded_payload['root_username'],
            azure_access_key_id=req.azure_access_key_id,
            s3_access_key_id=req.s3_access_key_id,
            s3_secret_access_key=req.s3_secret_access_key,
            s3_region_name=req.s3_region_name,
        ))
    except Exception as e:
        print(f"Error Renewing Licence: {e}")
        raise HTTPException(status_code=404, detail="Unable to renew licence")
