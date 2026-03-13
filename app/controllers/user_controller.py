"""
User Controller - Business Logic for User Operations
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.utils.password import hash_password, verify_password
from app.utils.jwt_utils import create_access_token


def register_user(db: Session, user_data: UserCreate) -> UserResponse:
    """
    Register a new user
    
    Args:
        db: Database session
        user_data: User registration data
        
    Returns:
        UserResponse: Created user data
        
    Raises:
        ValueError: If email already exists
    """
    try:
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create new user
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
    
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Email '{user_data.email}' is already registered")
    except Exception as e:
        db.rollback()
        raise Exception(f"Error registering user: {str(e)}")


def login_user(db: Session, user_data: UserLogin) -> dict:
    """
    Login a user and generate access token
    
    Args:
        db: Database session
        user_data: User login credentials
        
    Returns:
        dict: Access token and user data
        
    Raises:
        ValueError: If credentials are invalid
    """
    # Get user by email
    db_user = get_user_by_email(db, email=user_data.email)
    
    if not db_user:
        raise ValueError("Invalid email or password")
    
    # Verify password
    if not verify_password(user_data.password, db_user.password):
        raise ValueError("Invalid email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }


def get_user_by_email(db: Session, email: str) -> User:
    """
    Get user by email
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User: User object or None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Get user by ID
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User: User object or None
    """
    return db.query(User).filter(User.id == user_id).first()
