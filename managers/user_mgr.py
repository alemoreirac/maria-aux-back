from firebase_admin import credentials, initialize_app, auth
import os
from dotenv import load_dotenv
import json
load_dotenv()
import firebase_admin
from managers.credits_mgr import set_credits

NEW_USER_CREDIT = 2

env = os.getenv("ENV")

if env == "prod": 
    # Get the FIREBASE_CREDENTIALS string from the environment variable
    firebase_credentials_json_string = os.getenv("FIREBASE_CREDENTIALS")

    # Check if the environment variable is set
    if not firebase_credentials_json_string:
        raise ValueError("FIREBASE_CREDENTIALS environment variable is not set. Please set it in your .env file or production environment.")

    # Parse the JSON string into a Python dictionary
    try:
        cred_dict = json.loads(firebase_credentials_json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse FIREBASE_CREDENTIALS JSON string: {e}. Ensure it's valid JSON and newlines are escaped (\\n).")

else:    
    with open('firebase-credentials.json', 'r') as f:
        cred_dict = json.load(f)

try:
    cred = credentials.Certificate(cred_dict)
    initialize_app(cred)
except Exception as e:
    raise ValueError(f"Failed to initialize Firebase Admin SDK with provided credentials: {e}. Check the 'private_key' content for validity.")


class UserManager:
   
    async def create_user(self, email, password):
        user = auth.create_user(email=email, password=password)
        auth.generate_email_verification_link(email)
        
        await set_credits(user.uid,NEW_USER_CREDIT)  
        
        return user
    
    def get_user(self, uid):
        return auth.get_user(uid)
    
    def update_user(self, uid, **kwargs):
        return auth.update_user(uid, **kwargs)
    
    def delete_user(self, uid):
        return auth.delete_user(uid)
    
    def verify_token(self, token):
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception:
            return None
 