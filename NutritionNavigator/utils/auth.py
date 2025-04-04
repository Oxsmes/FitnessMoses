import streamlit as st
from models.database import User, SessionLocal
from sqlalchemy.orm import Session
from typing import Optional

def init_session_state():
    """Initialize session state variables for authentication"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

def login_user(db: Session, username: str, password: str) -> bool:
    """Authenticate user and set session state"""
    try:
        print(f"Attempting login for user: {username}")  # Debug log
        user = db.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            st.session_state.user_id = user.id
            st.session_state.username = user.username
            st.session_state.is_authenticated = True
            print(f"Login successful for user: {username}")  # Debug log
            return True
        print(f"Login failed for user: {username}")  # Debug log
        return False
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return False

def logout_user():
    """Clear user session state"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_authenticated = False

def register_user(
    db: Session,
    username: str,
    email: str,
    password: str
) -> Optional[User]:
    """Register a new user"""
    try:
        print(f"Attempting to register user: {username}")  # Debug log

        # Validate input
        if not username or not email or not password:
            raise ValueError("All fields are required")

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        # Check if username or email already exists
        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already taken")
        if db.query(User).filter(User.email == email).first():
            raise ValueError("Email already registered")

        # Create new user
        user = User(
            username=username,
            email=email,
            is_active=True
        )
        user.set_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Successfully registered user: {username}")  # Debug log
        return user
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")  # Debug log
        raise Exception(f"Registration error: {str(e)}")

def get_current_user(db: Session) -> Optional[User]:
    """Get the current logged-in user"""
    if st.session_state.is_authenticated and st.session_state.user_id:
        return db.query(User).filter(User.id == st.session_state.user_id).first()
    return None

def require_auth():
    """Decorator to require authentication"""
    if not st.session_state.is_authenticated:
        st.error("Please log in to access this feature")
        st.stop()