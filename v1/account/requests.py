import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import auth
from django.contrib.auth.models import User
import uuid 
import binascii

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred = credentials.Certificate(os.path.join(BASE_DIR,"account\\ezfx-c18ed-firebase-adminsdk-f5qcj-d96888755a.json"))
firebase_admin.initialize_app(cred)


demo_token="demotoken12345"

def getFirebaseUser(token):
    profile={"name":"","email":"","phone":"","uid":"","provider":""}
    if(token and token != demo_token): #If token is not null and is not the demo_token get Firebase user
        try:
            #Decode token
            decoded_token=auth.verify_id_token(token)
            #Get user uid
            uid=decoded_token["uid"]
            #Get UserRecord
            user=auth.get_user(uid)
    
            #Set profile info
            profile['uid']=uid
            profile['name']=user.display_name
            profile['phone']=user.phone_number
            profile['email']=user.email
            profile['provider']=user.provider_data[0].provider_id if(len(user.provider_data)>0) else "firebase" #check for anon signin
            
        except Exception as e:
            print(e)
    return profile

