from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.cognito import create_cognito_user, get_current_user, staff_required
from src.schemas.employee import EmployeeCreate, EmployeeResponse
from src.services.employee import EmployeeService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)


@router.get("/me", response_model=Dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information from the token
    """
    return current_user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    employee: EmployeeCreate,
    current_user: dict = Depends(staff_required),
):
    """
    Register a new employee (requires staff or admin permission)
    """
    # Create user in Cognito
    create_cognito_user(
        email=employee.contact_info,
        name=employee.name,
        role=employee.role,
    )
    
    # Return success response
    return {
        "status": "success",
        "message": f"User {employee.name} registered successfully",
    }


@router.get("/verify", response_model=Dict)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify authentication token
    """
    return {
        "status": "success",
        "message": "Token is valid",
        "user": current_user,
    }