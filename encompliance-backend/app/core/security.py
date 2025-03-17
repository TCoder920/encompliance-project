from cryptography.fernet import Fernet
import os
import base64
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Load environment variables
load_dotenv()

# Get encryption key from environment or generate one
def get_encryption_key():
    """Get or generate encryption key for API keys"""
    key = os.getenv("ENCRYPTION_KEY")
    
    if not key:
        # If no key exists, generate one and warn (in production this should be set)
        print("WARNING: No ENCRYPTION_KEY environment variable found. Generating a temporary one.")
        print("In production, set a permanent ENCRYPTION_KEY in your environment variables.")
        
        # Derive a key from the JWT secret key (not ideal but better than hardcoding)
        jwt_secret = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_for_development_only")
        salt = b'encompliance_salt'  # In production, this should be a proper random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(jwt_secret.encode()))
        
    # If key is not already base64 encoded properly, encode it
    if not isinstance(key, bytes):
        key = key.encode()
        
    try:
        # Validate that the key is proper Fernet key format
        Fernet(key)
        return key
    except Exception:
        # If not a proper key, derive one
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'emergency_salt',
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key))
        return derived_key

# Get the encryption key
ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key before storing it"""
    if not api_key:
        return None
    
    encrypted_key = cipher_suite.encrypt(api_key.encode())
    return encrypted_key.decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    """Decrypt a stored API key"""
    if not encrypted_api_key:
        return None
    
    try:
        decrypted_key = cipher_suite.decrypt(encrypted_api_key.encode())
        return decrypted_key.decode()
    except Exception as e:
        print(f"Error decrypting API key: {str(e)}")
        return None 