import uuid
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.schemas.auth_schema import (
    UserSignupRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    UserAuthResponse,
    ChangePasswordRequest,
    UserDetailsResponse,
)
from app.core.security import hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    """
    Registers a new user into PostgreSQL (modeldb):
    Validates name, email, and password. Checks if email is already registered.
    """
    email_clean = request.email.strip().lower()
    name_clean = request.name.strip()

    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "field": "email",
                "message": "This email is already registered. Redirecting you to login...",
                "already_registered": True
            }
        )

    # Securely hash password
    hashed_pwd = hash_password(request.password)

    # Create new user record
    new_user = User(
        name=name_clean,
        email=email_clean,
        password_hash=hashed_pwd,
        avatar_url=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Registered new user in modeldb: {new_user.email} (id: {new_user.id})")

    token = f"jwt_omni_{uuid.uuid4().hex}"
    return UserAuthResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        avatar_url=new_user.avatar_url,
        token=token,
        auth_provider="email",
        message="Account created successfully."
    )

@router.post("/login", response_model=UserAuthResponse, status_code=status.HTTP_200_OK)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user against PostgreSQL (modeldb):
    Verifies email and password, returning field-specific validation errors.
    """
    query_str = request.email.strip().lower()

    # 1. Lookup by email or name
    user = db.query(User).filter(
        (User.email == query_str) | (User.name.ilike(request.email.strip()))
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"field": "email", "message": "No account found with this email address."}
        )

    # 2. Check password
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"field": "password", "message": "Incorrect password. Please try again."}
        )

    logger.info(f"User logged in successfully: {user.email}")
    token = f"jwt_omni_{uuid.uuid4().hex}"

    return UserAuthResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        token=token,
        auth_provider="email" if user.password_hash else "google",
        message="Login successful."
    )

@router.post("/google", response_model=UserAuthResponse, status_code=status.HTTP_200_OK)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Handles Firebase Google Sign-In:
    - Captures Google full name, email, and Google profile picture.
    - Saves and updates in PostgreSQL (modeldb).
    - If called from Sign Up page (`is_signup=True`) and user already exists, notifies that the email is already registered.
    """
    email_clean = request.email.strip().lower()
    name_clean = request.name.strip() if request.name else "Google User"
    photo_url = request.photo_url.strip() if request.photo_url else None

    user = db.query(User).filter(User.email == email_clean).first()

    if user and request.is_signup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "field": "email",
                "message": "This Google account is already registered. Redirecting to login...",
                "already_registered": True
            }
        )

    if not user:
        user = User(
            name=name_clean,
            email=email_clean,
            password_hash=None,
            avatar_url=photo_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Provisioned new user via Google with avatar in modeldb: {user.email}")
    else:
        # Update name and avatar if provided by Google
        if photo_url and user.avatar_url != photo_url:
            user.avatar_url = photo_url
        if name_clean and user.name != name_clean:
            user.name = name_clean
        db.commit()
        db.refresh(user)
        logger.info(f"Updated user via Google in modeldb: {user.email}")

    token = f"jwt_omni_g_{uuid.uuid4().hex}"
    return UserAuthResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        token=token,
        auth_provider="google",
        message="Google authentication successful."
    )

@router.get("/user/{user_id}", response_model=UserDetailsResponse)
def get_user_details(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve user details for profile screen including authentication provider.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found."}
        )

    provider = "google" if not user.password_hash else "email"
    return UserDetailsResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        auth_provider=provider,
        created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
    )

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    """
    Changes user's password if registered with email/password.
    Google OAuth accounts cannot change password via this endpoint.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"field": "current_password", "message": "User not found."}
        )

    # Google users do not have a password_hash
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "field": "general",
                "message": "This account was created via Google. Password change is managed through Google."
            }
        )

    # Verify current password
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "current_password", "message": "The current password you entered is incorrect."}
        )

    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "new_password", "message": "New password must be at least 6 characters long."}
        )

    # Hash new password and save
    user.password_hash = hash_password(request.new_password)
    db.commit()
    logger.info(f"Password updated successfully for user: {user.email}")

    return {"status": "success", "message": "Password changed successfully."}
