import os
import shutil
import datetime
import sqlite3
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"
DB_PATH = BASE_DIR / "app.db"
PDF_STORAGE_PATH = BASE_DIR / "pdf_storage"

def add_pdf_direct():
    """Add the test PDF directly to the database"""
    
    # Check if the test PDF exists
    test_pdf_path = RESOURCES_DIR / "test_compliance.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"Error: Test PDF not found at {test_pdf_path}")
        print("Please run test_pdf_context.py first to create the test PDF")
        return None
    
    # Create storage directory if it doesn't exist
    os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
    
    # Generate a unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = f"{timestamp}_test_compliance.pdf"
    
    # Copy the test PDF to the storage location
    dest_path = PDF_STORAGE_PATH / unique_filename
    shutil.copyfile(test_pdf_path, dest_path)
    
    # Get file size
    file_size = os.path.getsize(dest_path)
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get a test user ID
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id_result = cursor.fetchone()
        
        if not user_id_result:
            print("Error: No users found in the database")
            return None
        
        user_id = user_id_result[0]
        
        # Insert the document record
        now = datetime.datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO documents (filename, filepath, file_type, file_size, uploaded_at, uploaded_by, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test_compliance.pdf", unique_filename, "PDF", file_size, now, user_id, 0)
        )
        
        # Get the ID of the inserted document
        doc_id = cursor.lastrowid
        
        # Commit the transaction
        conn.commit()
        
        print(f"Added test PDF to database with ID: {doc_id}")
        print(f"Filename: test_compliance.pdf")
        print(f"Stored at: {dest_path}")
        
        return doc_id
    
    except Exception as e:
        print(f"Error adding test PDF to database: {str(e)}")
        import traceback
        print(traceback.format_exc())
        conn.rollback()
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    doc_id = add_pdf_direct()
    if doc_id:
        print(f"Test PDF added successfully with ID: {doc_id}")
        print(f"You can now use this document ID in the chat by including it in the document_ids parameter")
    else:
        print("Failed to add test PDF to database") 