from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ServiceType(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    
class GenerateLicenceRequest(BaseModel):
    mail_id: str
    service_type: ServiceType
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    azure_access_key_id: Optional[str] = None
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_region_name: Optional[str] = None
    
class RenewLicenceRequest(BaseModel):
    
    service_type: ServiceType
    licence_token: str
    public_key: str
    
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    
    azure_access_key_id: Optional[str] = None
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_region_name: Optional[str] = None
    
class LicenceRequest(BaseModel):

    account_id: Optional[str] = None
    subscriber_id: Optional[str] = None
    subscription_id: Optional[str] = None

    service_type: Optional[str] = None
    root_user_id: Optional[str] = None
    root_username: Optional[str] = None
     
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    
    azure_access_key_id: Optional[str] = None
    
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_region_name: Optional[str] = None