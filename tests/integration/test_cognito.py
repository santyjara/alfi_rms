import boto3
import pytest
from botocore.exceptions import ClientError

from src.auth.cognito import create_cognito_user, delete_cognito_user
from src.auth.config import get_cognito_config


@pytest.fixture(scope="module")
def cognito_config():
    """Cognito configuration"""
    return get_cognito_config()


@pytest.fixture(scope="module")
def test_user_email():
    """Unique email for test user"""
    import uuid

    return f"test-{uuid.uuid4()}@example.com"


def test_real_create_and_delete_cognito_user(test_user_email, cognito_config):
    """Integration test with real Cognito - creates and deletes a real user"""
    # Test data
    test_name = "Integration Test User"
    test_family_name = "Jaramillo"
    test_role = "Staff"

    # 1. Create the user
    result = create_cognito_user(
        email=test_user_email,
        name=test_name,
        role=test_role,
        address="123 Test St",
        birthdate="1990-01-01",
        gender="Male",
        phone_number="+12345678900",
        family_name=test_family_name,
    )
    # Assert user was created successfully
    assert "User" in result
    attributes = result["User"]["Attributes"]
    assert [attr for attr in attributes if attr["Name"] == "email"][0][
        "Value"
    ] == test_user_email

    # 2. Verify user exists in Cognito
    # Get direct reference to cognito client (without importing)
    cognito_client = boto3.client(
        "cognito-idp",
        region_name=cognito_config.COGNITO_REGION,
        aws_access_key_id=cognito_config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cognito_config.AWS_SECRET_ACCESS_KEY,
    )

    # Try to get the user - will raise exception if not found
    user_details = cognito_client.admin_get_user(
        UserPoolId=cognito_config.COGNITO_USER_POOL_ID,
        Username=result["User"]["Username"],
    )
    # Check user exists and has expected attributes
    attributes = user_details["UserAttributes"]
    assert [attr for attr in attributes if attr["Name"] == "email"][0][
        "Value"
    ] == test_user_email

    # 3. Check the user is in the right group
    groups = cognito_client.admin_list_groups_for_user(
        UserPoolId=cognito_config.COGNITO_USER_POOL_ID,
        Username=user_details["Username"],
    )
    assert len(groups["Groups"]) > 0
    assert any(group["GroupName"] == test_role for group in groups["Groups"])

    # 4. Delete the user
    delete_cognito_user(test_user_email)

    # 5. Verify user no longer exists
    with pytest.raises(ClientError) as excinfo:
        cognito_client.admin_get_user(
            UserPoolId=cognito_config.COGNITO_USER_POOL_ID,
            Username=user_details["Username"],
        )

    # Check correct error is raised
    assert "UserNotFoundException" in str(excinfo.value)
