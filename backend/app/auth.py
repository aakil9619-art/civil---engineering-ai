import json, os
from fastapi import HTTPException
import firebase_admin
from firebase_admin import credentials, auth

def _init():
    if firebase_admin._apps:
        return
    raw=os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON","").strip()
    if not raw:
        raise RuntimeError("Firebase service account is not configured.")
    cred=credentials.Certificate(json.loads(raw))
    firebase_admin.initialize_app(cred)

def verify_bearer(authorization: str):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    _init()
    token=authorization.split(" ",1)[1].strip()
    if not token:
        raise RuntimeError("Authentication required.")
    try:
        return auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")

def public_config():
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY",""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN",""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID",""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET",""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID",""),
        "appId": os.getenv("FIREBASE_APP_ID",""),
        "enabled": all(os.getenv(k,"").strip() for k in [
            "FIREBASE_API_KEY","FIREBASE_AUTH_DOMAIN","FIREBASE_PROJECT_ID",
            "FIREBASE_MESSAGING_SENDER_ID","FIREBASE_APP_ID"
        ])
    }
