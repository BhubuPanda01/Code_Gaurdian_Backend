"""
User Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, LoginResponse
from app.controllers.user_controller import register_user, login_user, get_user_by_email, get_user_by_id
from app.utils.jwt_utils import get_user_id_from_token
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user data
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        user = register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login a user and return access token in cookies
    
    Args:
        user_data: User login credentials (email and password)
        db: Database session
        
    Returns:
        LoginResponse: Access token and user data
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        login_response = login_user(db, user_data)
        
        # Create response with token in cookies
        response = JSONResponse(
            content={
                "access_token": login_response["access_token"],
                "token_type": login_response["token_type"],
                "user": {
                    "id": login_response["user"].id,
                    "name": login_response["user"].name,
                    "email": login_response["user"].email,
                    "created_at": login_response["user"].created_at.isoformat(),
                    "updated_at": login_response["user"].updated_at.isoformat() if login_response["user"].updated_at else None
                }
            },
            status_code=status.HTTP_200_OK
        )
        
        # Set token in cookies
        response.set_cookie(
            key="access_token",
            value=login_response["access_token"],
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=86400  # 24 hours
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user(access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """
    Get current logged in user from access token in cookies
    
    Args:
        access_token: JWT token from cookies
        db: Database session
        
    Returns:
        UserResponse: Current user data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )
    
    # Extract user ID from token
    user_id = get_user_id_from_token(access_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    """
    Logout user by clearing the access token cookie
    
    Returns:
        dict: Logout success message
    """
    response = JSONResponse(
        content={"message": "Successfully logged out"},
        status_code=status.HTTP_200_OK
    )
    
    # Clear the access token cookie
    response.delete_cookie(key="access_token")
    
    return response

