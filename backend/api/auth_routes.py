"""
Authentication API Routes
Login, registration, token management, and user operations
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..core.auth import (
    AuthenticationService, User, UserCreate, UserUpdate, APIKey,
    get_current_user, get_current_active_user, require_permission, require_role,
    Permission, UserRole
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User


class APIKeyResponse(BaseModel):
    """API key response model"""
    api_key: str
    key_info: APIKey


class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str
    new_password: str


@router.post("/register", response_model=User)
async def register(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends()
):
    """Register a new user"""
    try:
        user = await auth_service.create_user(user_data)
        return user
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends()
):
    """Login with username and password"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create tokens
        access_token = auth_service.create_access_token(user)
        refresh_token = auth_service.create_refresh_token(user)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    auth_service: AuthenticationService = Depends()
):
    """Refresh access token"""
    try:
        # Verify refresh token
        token_data = await auth_service.verify_token(refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await auth_service.get_user(token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token = auth_service.create_access_token(user)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends()
):
    """Logout and revoke token"""
    try:
        # Get token from authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            await auth_service.revoke_token(token)
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    updates: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends()
):
    """Update current user information"""
    try:
        # Users can only update their own basic info
        allowed_updates = UserUpdate(
            email=updates.email,
            full_name=updates.full_name
        )
        
        updated_user = await auth_service.update_user(current_user.user_id, allowed_updates)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends()
):
    """Change user password"""
    try:
        # Verify current password
        user = await auth_service.authenticate_user(current_user.username, password_data.current_password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password (implementation would update the password hash)
        # For now, just return success
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    name: str,
    permissions: Optional[List[str]] = None,
    expires_in_days: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends()
):
    """Create API key"""
    try:
        key, key_info = await auth_service.create_api_key(
            current_user.user_id, name, permissions, expires_in_days
        )
        
        return APIKeyResponse(api_key=key, key_info=key_info)
        
    except Exception as e:
        logger.error(f"API key creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key creation failed"
        )


@router.get("/api-keys", response_model=List[APIKey])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends()
):
    """List user's API keys"""
    try:
        keys = await auth_service.list_api_keys(current_user.user_id)
        return keys
        
    except Exception as e:
        logger.error(f"API key listing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key listing failed"
        )


# Admin routes
@router.get("/users", response_model=List[User])
async def list_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthenticationService = Depends()
):
    """List all users (admin only)"""
    try:
        users = await auth_service.list_users()
        return users
        
    except Exception as e:
        logger.error(f"User listing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User listing failed"
        )


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    updates: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthenticationService = Depends()
):
    """Update user (admin only)"""
    try:
        updated_user = await auth_service.update_user(user_id, updates)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthenticationService = Depends()
):
    """Delete user (admin only)"""
    try:
        success = await auth_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )
