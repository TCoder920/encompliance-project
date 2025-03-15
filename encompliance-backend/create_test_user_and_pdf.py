import os
import shutil
import datetime
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.user import User
from app.models.document import Document
from app.core.config import get_settings
from app.auth.utils import get_password_hash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

settings = get_settings()

# Convert PostgreSQL URL to AsyncIO format
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    'postgresql://', 'postgresql+asyncpg://'
)

async def create_test_pdf():
    """Create a test PDF file in memory"""
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
    return buffer.getvalue()

async def ensure_test_user(session):
    """Ensure a test user exists in the database"""
    # Check if test user already exists
    result = await session.execute(
        select(User).where(User.email == "test@example.com")
    )
    test_user = result.scalars().first()
    
    if not test_user:
        print("Creating test user...")
        # Create a test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_verified=True
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        print(f"Created test user with ID: {test_user.id}")
    else:
        print(f"Test user already exists with ID: {test_user.id}")
    
    return test_user

async def add_test_pdf_to_db():
    """Add a test PDF to the database"""
    # Create async engine and session
    engine = create_async_engine(ASYNC_DATABASE_URL)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        try:
            # Ensure we have a test user
            test_user = await ensure_test_user(session)
            
            # Create PDF storage directory if it doesn't exist
            os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
            
            # Create a test PDF in memory
            pdf_content = await create_test_pdf()
            
            # Generate a unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{timestamp}_test_compliance.pdf"
            
            # Save the PDF to the storage location
            dest_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
            with open(dest_path, "wb") as f:
                f.write(pdf_content)
            
            # Get file size
            file_size = os.path.getsize(dest_path)
            
            # Create a Document record in the database
            document = Document(
                filename="test_compliance.pdf",
                filepath=unique_filename,
                file_type="PDF",
                file_size=file_size,
                uploaded_by=test_user.id
            )
            session.add(document)
            await session.commit()
            await session.refresh(document)
            
            print(f"Added test PDF with ID: {document.id}")
            print(f"Filename: {document.filename}")
            print(f"Stored at: {dest_path}")
            
            return document.id
        
        except Exception as e:
            print(f"Error adding test PDF: {str(e)}")
            import traceback
            print(traceback.format_exc())
            await session.rollback()
            return None

async def main():
    """Main function"""
    doc_id = await add_test_pdf_to_db()
    if doc_id:
        print(f"Test PDF added successfully with ID: {doc_id}")
        print(f"You can now use this document ID in the chat by including it in the document_ids parameter")
    else:
        print("Failed to add test PDF to database")

if __name__ == "__main__":
    asyncio.run(main()) 