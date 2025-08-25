"""
Authentication and Authorization System
Comprehensive security implementation with JWT, RBAC, and API key management
"""

import asyncio
import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

import bcrypt
import jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field

from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class UserRole(str):
    """User role definitions"""
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"
    API_CLIENT = "api_client"


class Permission(str):
    """Permission definitions"""
    # Agent permissions
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"
    
    # Browser automation permissions
    BROWSER_NAVIGATE = "browser:navigate"
    BROWSER_INTERACT = "browser:interact"
    BROWSER_SCREENSHOT = "browser:screenshot"
    BROWSER_SCRAPE = "browser:scrape"
    
    # MCP permissions
    MCP_LIST_TOOLS = "mcp:list_tools"
    MCP_CALL_TOOL = "mcp:call_tool"
    MCP_MANAGE_SERVERS = "mcp:manage_servers"
    
    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIG = "system:config"
    
    # API permissions
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"


class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = UserRole.USER
    permissions: List[str] = []
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = UserRole.USER


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class APIKey(BaseModel):
    """API key model"""
    key_id: str
    user_id: str
    name: str
    key_hash: str
    permissions: List[str] = []
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: int = 1000  # requests per hour
    metadata: Dict[str, Any] = {}


class TokenData(BaseModel):
    """JWT token data"""
    user_id: str
    username: str
    role: str
    permissions: List[str]
    exp: datetime
    iat: datetime
    jti: str  # JWT ID


class AuthenticationService:
    """Authentication and authorization service"""
    
    def __init__(self, session_manager: SessionManager, secret_key: str):
        self.session_manager = session_manager
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # In-memory stores (in production, use database)
        self.users: Dict[str, User] = {}
        self.user_passwords: Dict[str, str] = {}  # user_id -> hashed_password
        self.api_keys: Dict[str, APIKey] = {}
        self.revoked_tokens: set = set()
        
        # Role-based permissions
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.SYSTEM_ADMIN,
                Permission.SYSTEM_MONITOR,
                Permission.SYSTEM_CONFIG,
                Permission.AGENT_CREATE,
                Permission.AGENT_READ,
                Permission.AGENT_UPDATE,
                Permission.AGENT_DELETE,
                Permission.AGENT_EXECUTE,
                Permission.BROWSER_NAVIGATE,
                Permission.BROWSER_INTERACT,
                Permission.BROWSER_SCREENSHOT,
                Permission.BROWSER_SCRAPE,
                Permission.MCP_LIST_TOOLS,
                Permission.MCP_CALL_TOOL,
                Permission.MCP_MANAGE_SERVERS,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.API_ADMIN
            ],
            UserRole.USER: [
                Permission.AGENT_READ,
                Permission.AGENT_EXECUTE,
                Permission.BROWSER_NAVIGATE,
                Permission.BROWSER_INTERACT,
                Permission.BROWSER_SCREENSHOT,
                Permission.MCP_LIST_TOOLS,
                Permission.MCP_CALL_TOOL,
                Permission.API_READ,
                Permission.API_WRITE
            ],
            UserRole.AGENT: [
                Permission.AGENT_EXECUTE,
                Permission.BROWSER_NAVIGATE,
                Permission.BROWSER_INTERACT,
                Permission.BROWSER_SCREENSHOT,
                Permission.BROWSER_SCRAPE,
                Permission.MCP_LIST_TOOLS,
                Permission.MCP_CALL_TOOL
            ],
            UserRole.API_CLIENT: [
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.AGENT_EXECUTE,
                Permission.MCP_LIST_TOOLS,
                Permission.MCP_CALL_TOOL
            ]
        }
        
        # Create default admin user
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_id = "admin-" + str(uuid.uuid4())
        admin_user = User(
            user_id=admin_id,
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            permissions=self.role_permissions[UserRole.ADMIN],
            is_active=True,
            is_verified=True
        )
        
        # Default password: "admin123" (change in production)
        default_password = "admin123"
        hashed_password = self._hash_password(default_password)
        
        self.users[admin_id] = admin_user
        self.user_passwords[admin_id] = hashed_password
        
        logger.info("Created default admin user (username: admin, password: admin123)")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _generate_api_key(self) -> tuple[str, str]:
        """Generate API key and its hash"""
        # Generate a secure random key
        key = f"ak_{secrets.token_urlsafe(32)}"
        
        # Create hash for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        return key, key_hash
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if username or email already exists
            for user in self.users.values():
                if user.username == user_data.username:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already exists"
                    )
                if user.email == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
            
            # Create user
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                permissions=self.role_permissions.get(user_data.role, [])
            )
            
            # Hash password
            hashed_password = self._hash_password(user_data.password)
            
            # Store user
            self.users[user_id] = user
            self.user_passwords[user_id] = hashed_password
            
            logger.info(f"Created user: {user.username} ({user_id})")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        try:
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                return None
            
            # Check if user is active
            if not user.is_active:
                return None
            
            # Verify password
            hashed_password = self.user_passwords.get(user.user_id)
            if not hashed_password or not self._verify_password(password, hashed_password):
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        token_data = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "permissions": user.permissions,
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4())
        }
        
        token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        token_data = {
            "user_id": user.user_id,
            "type": "refresh",
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4())
        }
        
        token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        return token
    
    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            # Check if token is revoked
            if token in self.revoked_tokens:
                return None
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract token data
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            # Check if user exists and is active
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return None
            
            # Create token data
            token_data = TokenData(
                user_id=user_id,
                username=payload.get("username", ""),
                role=payload.get("role", ""),
                permissions=payload.get("permissions", []),
                exp=datetime.fromtimestamp(payload.get("exp", 0)),
                iat=datetime.fromtimestamp(payload.get("iat", 0)),
                jti=payload.get("jti", "")
            )
            
            return token_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def revoke_token(self, token: str):
        """Revoke a JWT token"""
        self.revoked_tokens.add(token)
    
    async def create_api_key(self, user_id: str, name: str, permissions: List[str] = None, expires_in_days: int = None) -> tuple[str, APIKey]:
        """Create API key for user"""
        try:
            # Check if user exists
            user = self.users.get(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Generate API key
            key, key_hash = self._generate_api_key()
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create API key record
            key_id = str(uuid.uuid4())
            api_key = APIKey(
                key_id=key_id,
                user_id=user_id,
                name=name,
                key_hash=key_hash,
                permissions=permissions or user.permissions,
                expires_at=expires_at
            )
            
            # Store API key
            self.api_keys[key_id] = api_key
            
            logger.info(f"Created API key: {name} for user {user.username}")
            return key, api_key
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise
    
    async def verify_api_key(self, key: str) -> Optional[APIKey]:
        """Verify API key"""
        try:
            # Hash the provided key
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            
            # Find matching API key
            for api_key in self.api_keys.values():
                if api_key.key_hash == key_hash and api_key.is_active:
                    # Check expiration
                    if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
                        api_key.is_active = False
                        return None
                    
                    # Update usage
                    api_key.last_used = datetime.utcnow()
                    api_key.usage_count += 1
                    
                    return api_key
            
            return None
            
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return None
    
    def check_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        return required_permission in user_permissions or Permission.SYSTEM_ADMIN in user_permissions
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    async def update_user(self, user_id: str, updates: UserUpdate) -> Optional[User]:
        """Update user"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Update fields
        if updates.email is not None:
            user.email = updates.email
        if updates.full_name is not None:
            user.full_name = updates.full_name
        if updates.role is not None:
            user.role = updates.role
            user.permissions = self.role_permissions.get(updates.role, [])
        if updates.permissions is not None:
            user.permissions = updates.permissions
        if updates.is_active is not None:
            user.is_active = updates.is_active
        
        user.updated_at = datetime.utcnow()
        
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id in self.users:
            del self.users[user_id]
            if user_id in self.user_passwords:
                del self.user_passwords[user_id]
            
            # Remove user's API keys
            keys_to_remove = [k for k, v in self.api_keys.items() if v.user_id == user_id]
            for key_id in keys_to_remove:
                del self.api_keys[key_id]
            
            return True
        return False
    
    async def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())
    
    async def list_api_keys(self, user_id: str) -> List[APIKey]:
        """List API keys for user"""
        return [key for key in self.api_keys.values() if key.user_id == user_id]


# Security dependencies
security = HTTPBearer()

def get_auth_service() -> AuthenticationService:
    """Get authentication service instance"""
    # This would be injected from the main application
    # For now, return a placeholder
    return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user"""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    token = credentials.credentials
    token_data = await auth_service.verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await auth_service.get_user(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        auth_service: AuthenticationService = Depends(get_auth_service)
    ):
        if not auth_service.check_permission(current_user.permissions, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    
    return permission_checker

def require_role(role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        return current_user
    
    return role_checker
