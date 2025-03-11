import logging
import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import Base, engine
from app.models.user import User
from app.models.role import Role
from app.schemas.role import RoleEnum

logger = logging.getLogger(__name__)

# Create roles
def create_initial_roles(db: Session) -> None:
    for role in RoleEnum:
        db_role = db.query(Role).filter(Role.name == role.value).first()
        if not db_role:
            db_role = Role(name=role.value)
            db.add(db_role)
    db.commit()

# Create storage directories
def create_storage_directories() -> None:
    # Create PDF storage directory
    pdf_storage_path = Path(settings.PDF_STORAGE_PATH)
    pdf_storage_path.mkdir(parents=True, exist_ok=True)
    
    # Create directory for models if not using placeholder
    if settings.USE_LOCAL_AI:
        model_path = Path(settings.AI_MODEL_PATH).parent
        model_path.mkdir(parents=True, exist_ok=True)

def init_db(db: Session) -> None:
    # Create tables
    logger.info("Creating tables")
    Base.metadata.create_all(bind=engine)
    
    # Create initial roles
    logger.info("Creating initial roles")
    create_initial_roles(db)
    
    # Create storage directories
    logger.info("Creating storage directories")
    create_storage_directories()
    
    logger.info("Database initialized successfully") 