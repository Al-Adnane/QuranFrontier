"""JWT authentication and RBAC (Role-Based Access Control)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import hashlib
import os

from .models import UserRole

# Define HTTPAuthCredentials locally since fastapi.security doesn't export it
class HTTPAuthCredentials:
    def __init__(self, scheme: str, credentials: str):
        self.scheme = scheme
        self.credentials = credentials

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# In-memory user store (replace with database in production)
USERS_DB: Dict[str, Dict] = {
    "admin": {
        "user_id": "admin-001",
        "username": "admin",
        "email": "admin@quran.local",
        "password_hash": hashlib.sha256(b"admin-password").hexdigest(),
        "role": UserRole.ADMIN,
        "is_active": True
    },
    "scholar": {
        "user_id": "scholar-001",
        "username": "scholar",
        "email": "scholar@quran.local",
        "password_hash": hashlib.sha256(b"scholar-password").hexdigest(),
        "role": UserRole.SCHOLAR,
        "is_active": True
    },
    "researcher": {
        "user_id": "researcher-001",
        "username": "researcher",
        "email": "researcher@quran.local",
        "password_hash": hashlib.sha256(b"researcher-password").hexdigest(),
        "role": UserRole.RESEARCHER,
        "is_active": True
    }
}

# Token blacklist (in production, use Redis)
TOKEN_BLACKLIST = set()

security = HTTPBearer()


class TokenData:
    """JWT token payload."""
    def __init__(self, user_id: str, username: str, role: UserRole, exp: datetime):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.exp = exp


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password."""
    return hash_password(plain_password) == password_hash


def create_access_token(
    user_id: str,
    username: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, int]:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role.value,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "type": "access"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(user_id: str, username: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "type": "refresh"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> TokenData:
    """Verify JWT token and extract payload."""
    if token in TOKEN_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        role_str: str = payload.get("role")
        exp_timestamp: float = payload.get("exp")

        if user_id is None or username is None or role_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        role = UserRole(role_str)
        exp = datetime.fromtimestamp(exp_timestamp)

        return TokenData(user_id=user_id, username=username, role=role, exp=exp)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(credentials = Depends(security)) -> TokenData:
    """Dependency to get current authenticated user."""
    # credentials is an HTTPAuthCredentials-like object from HTTPBearer()
    token = credentials.credentials if hasattr(credentials, 'credentials') else credentials
    return verify_token(token)


def require_role(required_role: UserRole):
    """Dependency factory to require specific role."""
    def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        # Role hierarchy: ADMIN > SCHOLAR > RESEARCHER > PUBLIC
        role_hierarchy = {
            UserRole.PUBLIC: 0,
            UserRole.RESEARCHER: 1,
            UserRole.SCHOLAR: 2,
            UserRole.ADMIN: 3
        }

        if role_hierarchy[current_user.role] < role_hierarchy[required_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )

        return current_user

    return role_checker


def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_scholar_or_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require scholar or admin role."""
    if current_user.role not in [UserRole.SCHOLAR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scholar or Admin access required"
        )
    return current_user


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user by username and password."""
    user = USERS_DB.get(username)

    if user is None:
        return None

    if not user["is_active"]:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user


def create_user(username: str, email: str, password: str, role: UserRole) -> Dict:
    """Create new user."""
    if username in USERS_DB:
        raise ValueError("Username already exists")

    user_id = f"user-{len(USERS_DB) + 1:04d}"

    new_user = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

    USERS_DB[username] = new_user
    return new_user


def get_user(user_id: str) -> Optional[Dict]:
    """Get user by ID."""
    for user in USERS_DB.values():
        if user["user_id"] == user_id:
            return user
    return None


def list_users() -> list:
    """List all users."""
    return list(USERS_DB.values())


def update_user(user_id: str, **kwargs) -> Optional[Dict]:
    """Update user."""
    for username, user in USERS_DB.items():
        if user["user_id"] == user_id:
            for key, value in kwargs.items():
                if key == "role" and isinstance(value, str):
                    user[key] = UserRole(value)
                elif key != "password_hash":  # Don't allow direct password_hash update
                    user[key] = value
            return user
    return None


def delete_user(user_id: str) -> bool:
    """Delete user."""
    for username, user in list(USERS_DB.items()):
        if user["user_id"] == user_id:
            del USERS_DB[username]
            return True
    return False


def blacklist_token(token: str):
    """Add token to blacklist."""
    TOKEN_BLACKLIST.add(token)


class RateLimiter:
    """Simple rate limiter (use Redis in production)."""
    def __init__(self):
        self.requests: Dict[str, list] = {}

    def is_allowed(self, client_id: str, max_requests: int, window_seconds: int) -> bool:
        """Check if client is within rate limit."""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(seconds=window_seconds)

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff_time
        ]

        # Check limit
        if len(self.requests[client_id]) >= max_requests:
            return False

        # Add current request
        self.requests[client_id].append(now)
        return True


rate_limiter = RateLimiter()


def check_rate_limit(
    client_id: str,
    max_requests: int = 1000,
    window_seconds: int = 3600
) -> bool:
    """Check rate limit for client."""
    return rate_limiter.is_allowed(client_id, max_requests, window_seconds)


# ============================================================================
# PHASE 2: Security Hardening
# ============================================================================

import re
import redis as redis_lib
from fastapi import Request

# Initialize Redis for advanced rate limiting
redis_client = None

def init_redis():
    """Initialize Redis connection for rate limiting"""
    global redis_client
    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_client = redis_lib.Redis(host=redis_host, port=redis_port, decode_responses=True)
        redis_client.ping()
        return True
    except Exception as e:
        return False


class QueryValidator:
    """Prevent SQL injection and malicious queries"""

    DANGEROUS_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE",
        "INSERT INTO", "UPDATE", "EXEC", "EXECUTE",
        "DECLARE", "DEFINE", "BEGIN", "GRANT", "REVOKE",
        "--", "/*", "*/", "xp_", "sp_", "0x", "';", "1'"
    ]

    MAX_QUERY_LENGTH = 1000
    # Allow: words, spaces, hyphens, common punctuation (but not single quotes that could enable injection)
    ALLOWED_PATTERN = r"^[\w\s\-،؟!.,?]*$"  # Removed single quotes

    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validate and sanitize user search query"""
        if not query:
            raise ValueError("Query cannot be empty")

        query = query.strip()

        if len(query) > QueryValidator.MAX_QUERY_LENGTH:
            raise ValueError(f"Query exceeds maximum length ({QueryValidator.MAX_QUERY_LENGTH})")

        query_upper = query.upper()
        for keyword in QueryValidator.DANGEROUS_KEYWORDS:
            if keyword in query_upper:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")

        if not re.match(QueryValidator.ALLOWED_PATTERN, query, re.UNICODE):
            raise ValueError("Query contains forbidden characters")

        return query

    @staticmethod
    def validate_verse_reference(surah: int, ayah: int) -> tuple:
        """Validate verse surah and ayah numbers"""
        if not (1 <= surah <= 114):
            raise ValueError(f"Surah must be 1-114, got {surah}")
        if not (1 <= ayah <= 286):
            raise ValueError(f"Ayah must be 1-286, got {ayah}")
        return surah, ayah


class InputValidator:
    """Validate all user inputs"""

    @staticmethod
    def validate_string(value: str, min_len: int = 1, max_len: int = 1000, name: str = "value") -> str:
        """Validate string input"""
        if not isinstance(value, str):
            raise ValueError(f"{name} must be string")
        if len(value) < min_len:
            raise ValueError(f"{name} too short (min: {min_len})")
        if len(value) > max_len:
            raise ValueError(f"{name} too long (max: {max_len})")
        return value.strip()

    @staticmethod
    def validate_integer(value: int, min_val: int = None, max_val: int = None, name: str = "value") -> int:
        """Validate integer input"""
        if not isinstance(value, int):
            raise ValueError(f"{name} must be integer")
        if min_val is not None and value < min_val:
            raise ValueError(f"{name} too small (min: {min_val})")
        if max_val is not None and value > max_val:
            raise ValueError(f"{name} too large (max: {max_val})")
        return value


class SecurityHeaders:
    """Add security headers to responses"""

    @staticmethod
    def get_security_headers() -> dict:
        """Return dictionary of security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

    @staticmethod
    async def security_headers_middleware(request: Request, call_next):
        """Middleware to add security headers"""
        response = await call_next(request)
        for header, value in SecurityHeaders.get_security_headers().items():
            response.headers[header] = value
        return response
