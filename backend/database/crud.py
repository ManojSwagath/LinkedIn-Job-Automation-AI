"""CRUD operations for database models"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.models import User, Resume, Application


class UserRepository:
    """User CRUD operations"""
    
    @staticmethod
    def create(db: Session, email: str, hashed_password: str, full_name: str = "") -> User:
        """Create a new user"""
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()  # type: ignore[assignment]
            db.commit()


class ResumeRepository:
    """Resume CRUD operations"""
    
    @staticmethod
    def create(db: Session, user_id: int, **kwargs) -> Resume:
        """Create a new resume"""
        resume = Resume(user_id=user_id, **kwargs)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    
    @staticmethod
    def get_by_user(db: Session, user_id: int) -> List[Resume]:
        """Get all resumes for a user"""
        return db.query(Resume).filter(Resume.user_id == user_id).all()
    
    @staticmethod
    def get_primary(db: Session, user_id: int) -> Optional[Resume]:
        """Get user's primary resume"""
        return db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.is_primary == True
        ).first()


class ApplicationRepository:
    """Application CRUD operations"""
    
    @staticmethod
    def create(db: Session, user_id: int, **kwargs) -> Application:
        """Create a new application"""
        application = Application(user_id=user_id, **kwargs)
        db.add(application)
        db.commit()
        db.refresh(application)
        return application
    
    @staticmethod
    def get_by_user(db: Session, user_id: int) -> List[Application]:
        """Get all applications for a user"""
        return db.query(Application).filter(Application.user_id == user_id).all()
