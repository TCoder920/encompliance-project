from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenData
from app.auth.utils import SECRET_KEY, ALGORITHM
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

def get_token_from_request(
    token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None),
    request: Request = None
) -> Optional[str]:
    """Extract token from various sources."""
    # Log headers for debugging
    if request:
        logger.info(f"Request headers: {request.headers}")
        # Check for token in query parameters
        token_param = request.query_params.get('token')
        if token_param:
            logger.info("Token found in query parameters")
            return token_param
    
    # Try to get token from OAuth2 scheme
    if token:
        logger.info("Token found from OAuth2 scheme")
        return token
    
    # Try to get token from Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        logger.info("Token found from Authorization header")
        return token
    
    # Try to get token from custom header
    if request and request.headers.get("x-token"):
        logger.info("Token found from custom x-token header")
        return request.headers.get("x-token")
    
    logger.warning("No token found in request")
    return None

async def get_current_user(
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> Union[User, None]:
    """Get the current user from the JWT token."""
    logger.info("--- BEGIN get_current_user ---")
    logger.info(f"Token received: {token[:15] if token else 'None'}...")
    
    if token is None:
        logger.warning("Authentication failed: No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        logger.info(f"Attempting to decode token: {token[:15]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token payload: {payload}")
        
        username: str = payload.get("sub")
        
        if username is None:
            logger.warning("Authentication failed: Token missing 'sub' claim")
            raise credentials_exception
            
        token_data = TokenData(username=username)
        logger.info(f"Token decoded successfully for user: {username}")
        
        # Check token expiration
        if 'exp' in payload:
            expiry = datetime.utcfromtimestamp(payload['exp'])
            now = datetime.utcnow()
            logger.info(f"Token expiry: {expiry}, Current time: {now}, Time until expiry: {expiry - now}")
            if now > expiry:
                logger.warning(f"Token expired at {expiry}")
                raise credentials_exception
                
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
        
    # Get the user from the database
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if user is None:
        logger.warning(f"User not found in database: {token_data.username}")
        raise credentials_exception
    
    logger.info(f"Found user: id={user.id}, username={user.username}, is_active={user.is_active}")
    logger.info("--- END get_current_user ---")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user is active."""
    if not current_user.is_active:
        logger.warning(f"Inactive user attempt: {current_user.username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 