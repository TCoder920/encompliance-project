import os
import shutil
from datetime import datetime
from app.database import SessionLocal
from app.models.pdf import PDF
from app.core.config import get_settings

settings = get_settings()

def add_test_pdf():
    """Add a test PDF to the database and storage directory"""
    
    # Create directory if it doesn't exist
    os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
    
    # Check if we have a test PDF in our resources
    test_pdf_path = "resources/test.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"Test PDF not found at: {test_pdf_path}")
        print("Creating a simple test PDF...")
        
        # Create a minimal PDF file using a Python library
        try:
            from reportlab.pdfgen import canvas
            
            # Create a PDF file
            pdf_filename = "test.pdf"
            c = canvas.Canvas(pdf_filename)
            c.drawString(100, 750, "This is a test PDF document for compliance regulations.")
            c.drawString(100, 735, "Child-to-caregiver ratio for 2-year-olds is 11:1.")
            c.drawString(100, 720, "All employees must undergo a background check.")
            c.drawString(100, 705, "Caregivers must complete 24 clock hours of training annually.")
            c.drawString(100, 690, "This document is for testing the PDF extraction functionality.")
            c.save()
            
            test_pdf_path = pdf_filename
            print(f"Created test PDF at: {test_pdf_path}")
        except Exception as e:
            print(f"Failed to create test PDF: {str(e)}")
            return
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = f"{timestamp}_test.pdf"
    dest_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
    
    # Copy the file to the storage directory
    shutil.copy(test_pdf_path, dest_path)
    print(f"Copied test PDF to: {dest_path}")
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create PDF record in database
        pdf = PDF(
            filename="test.pdf",
            filepath=unique_filename,
            uploaded_by=1  # Assuming user ID 1 exists
        )
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        
        print(f"Added PDF record to database: ID={pdf.id}, filepath={pdf.filepath}")
        print("Test PDF added successfully!")
        
        return pdf.id
    except Exception as e:
        print(f"Error adding PDF to database: {str(e)}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    add_test_pdf() 