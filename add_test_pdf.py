import os
import shutil
import datetime
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.pdf import PDF
from app.models.user import User
from app.core.config import get_settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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

def add_test_pdf():
    """
    Add a test PDF file to the database and storage directory
    """
    # Create DB session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Ensure we have a test user
        test_user = ensure_test_user(db)
        
        # Create storage directory if it doesn't exist
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Create a simple test PDF using reportlab if it doesn't exist
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")
        os.makedirs(resources_dir, exist_ok=True)
        test_pdf_path = os.path.join(resources_dir, "test.pdf")
        
        if not os.path.exists(test_pdf_path):
            print(f"Creating test PDF at {test_pdf_path}")
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica", 12)
            
            # Add a title
            c.drawString(100, 750, "Test Compliance Document")
            
            # Add some paragraphs of text
            paragraphs = [
                "This is a test PDF document for the compliance system.",
                "",
                "Compliance Regulations:",
                "1. All daycare facilities must maintain a 1:4 staff-to-child ratio for children under 2 years old.",
                "2. Staff members must have CPR certification renewed every 2 years.",
                "3. Background checks must be performed on all staff members annually.",
                "4. Facilities must have at least 35 square feet of indoor space per child.",
                "5. Fire drills must be conducted monthly and documented.",
                "6. All medications must be stored in locked cabinets.",
                "7. Food handling areas must be separate from diapering areas.",
                "8. Building must comply with local fire and safety codes.",
                "9. Emergency evacuation plans must be posted in visible locations.",
                "10. Daily health checks must be performed and documented for each child.",
                "",
                "Residential Care Compliance Requirements:",
                "1. Maintain a 1:6 staff-to-resident ratio during waking hours.",
                "2. Medication administration records must be maintained for all residents.",
                "3. Staff must complete 40 hours of training annually.",
                "4. Each resident must have an individualized care plan updated quarterly.",
                "5. Facilities must conduct and document monthly safety inspections.",
            ]
            
            y_position = 730
            for paragraph in paragraphs:
                y_position -= 20
                c.drawString(100, y_position, paragraph)
                if y_position < 100:
                    c.showPage()
                    y_position = 750
            
            c.save()
            
            # Save the PDF to the file
            with open(test_pdf_path, "wb") as f:
                f.write(buffer.getvalue())
        
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_test_compliance.pdf"
        
        # Copy the test PDF to the storage location
        dest_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
        shutil.copyfile(test_pdf_path, dest_path)
        
        # Create a PDF record in the database
        pdf = PDF(
            filename="test_compliance.pdf",
            filepath=unique_filename,
            uploaded_by=test_user.id
        )
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        
        print(f"Added test PDF with ID: {pdf.id}")
        print(f"Filename: {pdf.filename}")
        print(f"Stored at: {dest_path}")
        
        return pdf.id
    
    except Exception as e:
        print(f"Error adding test PDF: {str(e)}")
        import traceback
        print(traceback.format_exc())
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    pdf_id = add_test_pdf()
    if pdf_id:
        print(f"Test PDF added successfully with ID: {pdf_id}")
    else:
        print("Failed to add test PDF") 