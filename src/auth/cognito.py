from typing import Dict, List, Optional

import boto3
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi_cognito import CognitoAuth, CognitoSettings
from jose import JWTError, jwk, jwt
from pydantic import BaseModel

from src.auth.config import get_cognito_config

# Get Cognito configuration from environment variables
cognito_config = get_cognito_config()

# Configure Cognito settings
cognito_settings = CognitoSettings(
    region=cognito_config.region,
    user_pool_id=cognito_config.user_pool_id,
    client_id=cognito_config.client_id,
    client_secret=cognito_config.client_secret,
    domain=cognito_config.domain,
)

# Initialize CognitoAuth
cognito_auth = CognitoAuth(settings=cognito_settings)

# OAuth2 scheme for token validation
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{cognito_config.domain}/oauth2/authorize",
    tokenUrl=f"https://{cognito_config.domain}/oauth2/token",
    scopes={"email": "email access", "profile": "profile access"},
)


class TokenPayload(BaseModel):
    """Token payload model"""
    sub: str
    exp: int
    username: Optional[str] = None
    email: Optional[str] = None
    groups: List[str] = []
    

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate the token and return the current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode the token
        payload = await cognito_auth.verify_token(token)
        
        # Extract user information
        username = payload.get("username") or payload.get("email")
        if not username:
            raise credentials_exception
            
        # Extract user's groups/roles from the token
        groups = payload.get("cognito:groups", [])
        
        return {"username": username, "groups": groups, "sub": payload.get("sub")}
    except JWTError:
        raise credentials_exception


async def admin_required(current_user: dict = Depends(get_current_user)):
    """
    Check if the current user has admin privileges
    """
    if "admin" not in current_user.get("groups", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def staff_required(current_user: dict = Depends(get_current_user)):
    """
    Check if the current user has staff privileges (admin or staff)
    """
    allowed_groups = ["admin", "staff", "manager"]
    user_groups = current_user.get("groups", [])
    
    if not any(group in allowed_groups for group in user_groups):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


# Direct Cognito client for additional operations
cognito_client = boto3.client("cognito-idp", region_name=cognito_config.region)


def create_cognito_user(email: str, name: str, role: str = "staff"):
    """
    Create a new user in Cognito User Pool
    """
    try:
        response = cognito_client.admin_create_user(
            UserPoolId=cognito_config.user_pool_id,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "name", "Value": name},
                {"Name": "custom:role", "Value": role},
            ],
            MessageAction="SUPPRESS",  # Don't send welcome email
            TemporaryPassword=f"Temp123!",  # Temporary password
        )
        
        # Add user to appropriate group based on role
        if role in ["admin", "staff", "manager"]:
            cognito_client.admin_add_user_to_group(
                UserPoolId=cognito_config.user_pool_id,
                Username=email,
                GroupName=role,
            )
            
        return response
    except Exception as e:
        # Handle specific Cognito exceptions
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}",
        )


def delete_cognito_user(username: str):
    """
    Delete a user from Cognito User Pool
    """
    try:
        response = cognito_client.admin_delete_user(
            UserPoolId=cognito_config.user_pool_id,
            Username=username,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting user: {str(e)}",
        )