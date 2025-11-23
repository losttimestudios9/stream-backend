"""
Firebase configuration and utilities.
"""
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from firebase_admin.auth import UserRecord, UserNotFoundError
from fastapi import HTTPException, status
from .config import settings

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    try:
        # Get the service account key from settings
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Firebase: {str(e)}"
        )

# Firebase Auth functions
async def get_user(uid: str) -> Optional[UserRecord]:
    """Get a user by their Firebase UID."""
    try:
        return auth.get_user(uid)
    except UserNotFoundError:
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting user: {str(e)}"
        )

async def create_user(email: str, password: str, display_name: str = None) -> UserRecord:
    """Create a new Firebase user."""
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=False
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )

async def verify_id_token(token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token."""
    try:
        return auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Firestore functions
async def get_document(collection: str, doc_id: str) -> Dict[str, Any]:
    """Get a document from Firestore."""
    try:
        db = firestore.client()
        doc_ref = db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document: {str(e)}"
        )

# Storage functions
async def upload_file(file_path: str, destination_path: str) -> str:
    """Upload a file to Firebase Storage."""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(file_path)
        return blob.public_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

# Initialize Firebase when this module is imported
db, bucket = initialize_firebase()
