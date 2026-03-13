"""
Database Configuration Module
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    
)

# SQL Alchemy Configuration
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", False)
SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE", 5))
SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10))

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours

# API Configuration
API_TITLE = "Code Guardian API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Backend API for Code Guardian Application"
