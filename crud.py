from sqlalchemy.orm import Session

from auth import get_password_hash, verify_password
from models import User
from schemas import UserCreate


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session):
    return db.query(User).all()


def update_user(db: Session, user_id: int, updates: UserCreate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Optional: handle password hashing automatically if it's in the updates
    if updates.password:
        updates.password = get_password_hash(updates.password)

    for key, value in updates.model_dump().items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def create_user(db: Session, user_create: UserCreate):
    hashed_pw = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        password=hashed_pw,
        name=user_create.name,
        preferences=user_create.preferences.model_dump(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return False
    return user
