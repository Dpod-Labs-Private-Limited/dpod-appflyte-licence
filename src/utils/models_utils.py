from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ServiceType(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    
class GenerateLicenceRequest(BaseModel):
    mail_id: str
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    service_type: ServiceType
    
class RenewLicenceRequest(BaseModel):
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    service_type: ServiceType
    licence_token: str
    public_key: str
    
class LicenceRequest(BaseModel):
    aws_access_key_id:str
    aws_secret_access_key:str
    region_name:str
    account_id:str
    subscriber_id:str
    subscription_id:str
    root_user_id:str
    root_username:str
    service_type:str