# app/core/firebase.py
from typing import Optional, Tuple, Any
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from firebase_admin.auth import UserRecord, UserNotFoundError
from fastapi import HTTPException, status
from .config import settings

# Initialize variables
db = None
bucket = None

def initialize_firebase() -> Tuple[Any, Any]:
    """Initialize Firebase Admin SDK with service account credentials."""
    global db, bucket
    
    try:
        # Check if required Firebase settings are present
        if not all([
            settings.FIREBASE_TYPE,
            settings.FIREBASE_PROJECT_ID,
            settings.FIREBASE_PRIVATE_KEY,
            settings.FIREBASE_CLIENT_EMAIL
        ]):
            print("Warning: Firebase configuration is incomplete. Firebase features will be disabled.")
            return None, None

        firebase_credentials = {
            "type": settings.FIREBASE_TYPE,
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": settings.FIREBASE_AUTH_URI,
            "token_uri": settings.FIREBASE_TOKEN_URI,
            "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": settings.FIREBASE_CLIENT_CERT_URL
        }
        
        # Initialize the app with a service account
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred, {
            'storageBucket': f"{settings.FIREBASE_PROJECT_ID}.appspot.com"
        })
        
        # Initialize Firestore and Storage
        db = firestore.client()
        bucket = storage.bucket()
        
        return db, bucket
        
    except Exception as e:
        print(f"Warning: Failed to initialize Firebase: {str(e)}")
        return None, None

# Initialize Firebase on import
db, bucket = initialize_firebase()

# Update other functions to check if Firebase is initialized
async def get_user(uid: str) -> Optional[UserRecord]:
    """Get a user by their Firebase UID."""
    if not firebase_admin._apps:
        return None
    try:
        return auth.get_user(uid)
    except UserNotFoundError:
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting user: {str(e)}"
        )
