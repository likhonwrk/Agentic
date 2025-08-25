"""
User Management API Routes
CRUD operations for user management
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.auth import (
    AuthenticationService, User, UserCreate, UserUpdate,
    get_current_active_user, require_permission, Permission
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["user management"])


@router.get("/", response_model=List[User])
async def list_users(
    auth_service: AuthenticationService = Depends(),
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN))
):
    """List all users (admin only)"""
    try:
        return await auth_service.list_users()
    except Exception as e:
        logger.error(f"List users failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    auth_service: AuthenticationService = Depends(),
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN))
):
    """Get user by ID (admin only)"""
    user = await auth_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends(),
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN))
):
    """Create a new user (admin only)"""
    try:
        return await auth_service.create_user(user_data)
    except Exception as e:
        logger.error(f"Create user failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    updates: UserUpdate,
    auth_service: AuthenticationService = Depends(),
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN))
):
    """Update user (admin only)"""
    user = await auth_service.update_user(user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    auth_service: AuthenticationService = Depends(),
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN))
):
    """Delete user (admin only)"""
    success = await auth_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}
