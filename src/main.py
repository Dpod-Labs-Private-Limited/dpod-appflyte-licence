import jwt
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.services.licence_service import get_licence, generate_root_user_token
from src.services.aws_service import store_license
from src.utils.creds_utils import get_licence_creds
from src.utils.models_utils import GenerateLicenceRequest, LicenceRequest, RenewLicenceRequest

logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def handler(data: LicenceRequest):
    
    licence_details = get_licence(data)
    jwt_token =  licence_details["jwt_token"]
    public_key =  licence_details["public_key"]
    root_password = licence_details["root_password"]
    root_user_token = generate_root_user_token(jwt_token, public_key)
    subscription_id = data.subscription_id
    
    new_licence = {
        "LICENSE_TOKEN": jwt_token,
        "LICENSE_PUBLIC_KEY": public_key,
        "ROOT_USER_TOKEN": root_user_token,
        "ROOT_USER_NAME": data.root_username,
        "ROOT_PASSWORD": root_password
    }
    
    store_license(subscription_id, jwt_token, public_key, data.root_username, root_password)

    logger.info("Licence generated successfully...!")
    return new_licence
    
@app.post("/license/generate")
def generate_licence(req: GenerateLicenceRequest):
    try:
       
        account_details = get_licence_creds()    
        account_id = account_details["account_id"]
        subscriber_id = account_details["subscriber_id"]
        subscription_id = account_details["subscription_id"]
        root_user_id = account_details["user_id"]
                
        aws_access_key_id = req.aws_access_key_id
        aws_secret_access_key = req.aws_secret_access_key
        region_name = req.region_name
        root_username = req.mail_id
        service_type = req.service_type

        response = handler(LicenceRequest(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            account_id=account_id,
            subscriber_id=subscriber_id,
            subscription_id=subscription_id,
            root_user_id=root_user_id,
            root_username=root_username,
            service_type=service_type)
        )        
        return response

    except Exception as e:
        print(f"Error Generating Licence: {e}")
        raise HTTPException(status_code=404, detail="Unable to generate licence")
    
@app.post("/license/renew")
def renew_licence(req: RenewLicenceRequest):
    try:
           
        try:
            decoded_payload = jwt.decode(req.licence_token, req.public_key, algorithms=['HS256'], options={"verify_signature": False}, verify=False)
        except Exception as e:
            raise ValueError('License key not correctly formatted')
                
        account_id = decoded_payload['root_account_id']
        subscriber_id = decoded_payload['subscriber_id']
        subscription_id = decoded_payload['subscription_id']
        root_user_id = decoded_payload['root_user_id']
        root_username = decoded_payload['root_username']

        aws_access_key_id = req.aws_access_key_id
        aws_secret_access_key = req.aws_secret_access_key
        region_name = req.region_name
        service_type = req.service_type

        response = handler(LicenceRequest(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            account_id=account_id,
            subscriber_id=subscriber_id,
            subscription_id=subscription_id,
            root_user_id=root_user_id,
            root_username=root_username,
            service_type=service_type)
        )
        
        return response

    except Exception as e:
        print(f"Error Renewing Licence: {e}")
        raise HTTPException(status_code=404, detail="Unable to renew licence")