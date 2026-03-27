import uuid

def get_licence_creds():
    credentials = {
        "subscriber_id": str(uuid.uuid4()),
        "subscription_id": str(uuid.uuid4()),
        "account_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4())
    }
    return credentials