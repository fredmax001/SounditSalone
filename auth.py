from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import bcrypt
from database import get_db
from models import User, UserStatus, RefreshToken
from config import get_settings

settings = get_settings()


# Password hashing
# Monkey patch bcrypt for passlib compatibility
if not hasattr(bcrypt, '__about__'):
    class About:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = About()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT setup
security = HTTPBearer(auto_error=False)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for bcrypt version mismatch
        import bcrypt
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback for bcrypt version mismatch
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    # Preserve caller-provided token type; default to access only when absent.
    to_encode.setdefault("type", "access")
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_password_reset_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire, "type": "password_reset"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(db: Session, data: dict) -> str:
    """Create a refresh token with longer expiry and persist it server-side."""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    to_encode = {
        **data,
        "jti": jti,
        "exp": expire,
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    user_id = data.get("sub")
    if user_id is not None:
        token_hash = _hash_token(encoded_jwt)
        db.add(
            RefreshToken(
                jti=jti,
                user_id=int(user_id),
                token_hash=token_hash,
                expires_at=expire.replace(tzinfo=None),
            )
        )
        db.commit()

    return encoded_jwt


def decode_token(token: str, token_type: Optional[str] = None, verify_exp: bool = True) -> Optional[dict]:
    """Decode token with optional type verification."""
    try:
        options = {}
        if not verify_exp:
            options["verify_exp"] = False
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options=options)
        # Verify token type if specified
        if token_type and payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


def revoke_refresh_token(db: Session, jti: str) -> None:
    """Mark a refresh token as revoked."""
    token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if token and token.revoked_at is None:
        token.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()


def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> None:
    """Revoke every active refresh token for a user."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
        RefreshToken.expires_at > now,
    ).update({"revoked_at": now})
    db.commit()


def _get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """Read access token from Authorization header or HttpOnly cookie."""
    if credentials is not None:
        return credentials.credentials
    return request.cookies.get("access_token")


async def get_current_user(
    token: Optional[str] = Depends(_get_token_from_request),
    db: Session = Depends(get_db)
) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token, token_type="access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )
    
    return user


async def get_optional_user(
    token: Optional[str] = Depends(_get_token_from_request),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if token is None:
        return None

    payload = decode_token(token, token_type="access")
    
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None or user.status != UserStatus.ACTIVE:
        return None
        
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    from models import UserRole
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    from models import UserRole
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )
    return current_user


async def require_organizer(current_user: User = Depends(get_current_user)) -> User:
    from models import UserRole
    # ORGANIZER, VENUE, SPORT roles can manage events + admins
    if current_user.role not in [UserRole.ORGANIZER, UserRole.VENUE, UserRole.SPORT, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizer access required",
        )
    return current_user
