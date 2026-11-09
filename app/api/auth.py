import uuid
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.schemas.auth_schema import UserSignupRequest, UserLoginRequest, UserAuthResponse
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
            detail={"field": "email", "message": "An account with this email address already exists."}
        )

    # Securely hash password
    hashed_pwd = hash_password(request.password)

    # Create new user record
    new_user = User(
        name=name_clean,
        email=email_clean,
        password_hash=hashed_pwd
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
        token=token,
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
        token=token,
        message="Login successful."
    )

