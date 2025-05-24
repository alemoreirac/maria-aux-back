from firebase_admin import credentials, initialize_app, auth
import os
from dotenv import load_dotenv
import json
load_dotenv()
import firebase_admin

cred = credentials.Certificate("utils/firebase-creds.json")
initialize_app(cred)

class UserManager:
   
    def create_user(self, email, password):
        return auth.create_user(email=email, password=password)
    
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
 