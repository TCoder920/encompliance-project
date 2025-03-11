from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.role import RoleEnum


def get(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create(db: Session, *, obj_in: UserCreate) -> User:
    # Get the free role by default if not specified
    role_id = obj_in.role_id
    if not role_id:
        role = db.query(Role).filter(Role.name == RoleEnum.FREE.value).first()
        role_id = role.id if role else 1  # Fallback to ID 1 if role not found
    
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        operation_name=obj_in.operation_name,
        operation_type=obj_in.operation_type,
        state=obj_in.state,
        phone_number=obj_in.phone_number,
        is_active=obj_in.is_active,
        role_id=role_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in update_data:
        if field in update_data and hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, user_id: int) -> User:
    obj = db.query(User).get(user_id)
    db.delete(obj)
    db.commit()
    return obj


def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 