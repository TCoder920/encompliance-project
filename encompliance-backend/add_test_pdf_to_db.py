import os
import shutil
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Document
from app.models.user import User
from app.core.config import get_settings
from passlib.context import CryptContext

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def ensure_test_user(db_session):
    """
    Ensure that a test user exists in the database
    """
    test_email = "test@example.com"
    test_user = db_session.query(User).filter(User.email == test_email).first()
    
    if not test_user:
        print(f"Creating test user: {test_email}")
        # Create a test user
        test_user = User(
            email=test_email,
            username="testuser",
            hashed_password=pwd_context.hash("password123"),
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)
    
    return test_user

def add_test_pdf_to_db():
    """
    Add the test PDF to the database
    """
    # Create DB session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Ensure we have a test user
        test_user = ensure_test_user(db)
        
        # Check if the test PDF exists
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")
        test_pdf_path = os.path.join(resources_dir, "test_compliance.pdf")
        
        if not os.path.exists(test_pdf_path):
            print(f"Error: Test PDF not found at {test_pdf_path}")
            print("Please run test_pdf_context.py first to create the test PDF")
            return None
        
        # Create storage directory if it doesn't exist
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_test_compliance.pdf"
        
        # Copy the test PDF to the storage location
        dest_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
        shutil.copyfile(test_pdf_path, dest_path)
        
        # Get file size
        file_size = os.path.getsize(dest_path)
        
        # Create a Document record in the database
        document = Document(
            filename="test_compliance.pdf",
            filepath=os.path.join(settings.PDF_STORAGE_PATH, unique_filename),
            file_type="PDF",
            file_size=file_size,
            uploaded_by=test_user.id
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        print(f"Added test PDF to database with ID: {document.id}")
        print(f"Filename: {document.filename}")
        print(f"Stored at: {dest_path}")
        
        return document.id
    
    except Exception as e:
        print(f"Error adding test PDF to database: {str(e)}")
        import traceback
        print(traceback.format_exc())
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    doc_id = add_test_pdf_to_db()
    if doc_id:
        print(f"Test PDF added successfully with ID: {doc_id}")
        print(f"You can now use this document ID in the chat by including it in the document_ids parameter")
    else:
        print("Failed to add test PDF to database") 