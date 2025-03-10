from typing import List, Optional

import boto3
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi_cognito import CognitoAuth, CognitoSettings
from jose import JWTError
from pydantic import BaseModel

from src.auth.config import get_cognito_config

# Get Cognito configuration from environment variables
cognito_config = get_cognito_config()

# Configure Cognito settings
cognito_settings = CognitoSettings(
    check_expiration=True,
    jwt_header_prefix="Bearer",
    jwt_header_name="Authorization",
    userpools={
        "main": {
            "region": cognito_config.COGNITO_REGION,
            "userpool_id": cognito_config.COGNITO_USER_POOL_ID,
            "app_client_id": cognito_config.COGNITO_CLIENT_ID,
        }
    },
)

# Initialize CognitoAuth
cognito_auth = CognitoAuth(settings=cognito_settings)

# OAuth2 scheme for token validation
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{cognito_config.COGNITO_DOMAIN}/docs",
    tokenUrl=f"https://cognito-idp.{cognito_config.COGNITO_REGION}.amazonaws.com/{cognito_config.COGNITO_USER_POOL_ID}/.well-known/jwks.json",
    scopes={"email": "email access", "profile": "profile access"},
) # noqa


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
cognito_client = boto3.client(
    "cognito-idp",
    region_name=cognito_config.COGNITO_REGION,
    aws_access_key_id=cognito_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=cognito_config.AWS_SECRET_ACCESS_KEY,
)


def create_cognito_user(
    email: str,
    name: str,
    role: str = "staff",
    address: str = None,
    birthdate: str = None,
    gender: str = None,
    phone_number: str = None,
    given_name: str = None,
    family_name: str = None,
):
    """
    Create a new user in Cognito User Pool with required attributes

    Required attributes:
    - address
    - birthdate (format: YYYY-MM-DD)
    - gender
    - phone_number (format: +12345678900)
    - email
    - given_name
    - family_name
    """
    try:
        # Split name into given_name and family_name if not provided
        if not given_name or not family_name:
            name_parts = name.split(maxsplit=1)
            given_name = given_name or name_parts[0]
            family_name = family_name or (name_parts[1] if len(name_parts) > 1 else "")

        # Current timestamp for updated_at
        from datetime import datetime

        current_time = str(int(datetime.now().timestamp()))

        # Prepare user attributes
        user_attributes = [
            {"Name": "email", "Value": email},
            {"Name": "email_verified", "Value": "true"},
            {"Name": "given_name", "Value": given_name},
            {"Name": "family_name", "Value": family_name},
            {"Name": "name", "Value": name},
            {"Name": "updated_at", "Value": current_time},
        ]

        # Add required attributes if provided
        if address:
            user_attributes.append({"Name": "address", "Value": address})
        if birthdate:
            user_attributes.append({"Name": "birthdate", "Value": birthdate})
        if gender:
            user_attributes.append({"Name": "gender", "Value": gender})
        if phone_number:
            user_attributes.append({"Name": "phone_number", "Value": phone_number})

        response = cognito_client.admin_create_user(
            UserPoolId=cognito_config.COGNITO_USER_POOL_ID,
            Username=email,
            UserAttributes=user_attributes,
            MessageAction="SUPPRESS",  # Don't send welcome email
            TemporaryPassword="Temp12333332***!",  # Temporary password
        )

        # Add user to appropriate group based on role
        if role in ["Admin", "Staff", "Manager"]:
            cognito_client.admin_add_user_to_group(
                UserPoolId=cognito_config.COGNITO_USER_POOL_ID,
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
            UserPoolId=cognito_config.COGNITO_USER_POOL_ID,
            Username=username,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting user: {str(e)}",
        )
