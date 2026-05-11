import hmac
import hashlib
import jwt
import datetime
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class UtilityService:
    
    def generate_key_pair():
        # Generate a new RSA private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

        # Serialize the private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Generate the corresponding public key
        public_key = private_key.public_key()

        # Serialize the public key to PEM format
        public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

        # Create response
        response = {
            "private_key": private_pem.decode('utf-8'),
            "public_key": public_pem.decode('utf-8')
        }

        return response
    
    def get_stage():
        return 'dev'
  
    def generate_salt(key: str, value: str) -> str:
        # Encode the key and value to bytes
        key_bytes = key.encode('utf-8')
        value_bytes = value.encode('utf-8')

        # Create an HMAC object using the key and value
        hmac_obj = hmac.new(key_bytes, value_bytes, hashlib.sha256)

        # Generate the salt as a hexadecimal string
        salt = hmac_obj.hexdigest()

        return salt

    def create_jwt(payload, private_key, exp_date=None, algorithm='RS256'):
        if exp_date is None:
            exp_datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        else:
            if isinstance(exp_date, datetime.datetime):
                exp_datetime = exp_date
            elif isinstance(exp_date, datetime.date):
                exp_datetime = datetime.datetime.combine(exp_date, datetime.datetime.min.time())
            else:
                exp_datetime = datetime.datetime.strptime(exp_date, "%Y-%m-%d")

        payload['exp'] = int(exp_datetime.timestamp())
        token = jwt.encode(payload, private_key, algorithm=algorithm)
        return token
    
    def base64_url_encode(data):
        # Encode the data using Base64 encoding
        base64_str = base64.b64encode(data).decode('utf-8')

        # Replace Base64 characters with Base64URL characters
        base64_url_str = base64_str.replace('+', '-').replace('/', '_').rstrip('=')

        return base64_url_str

