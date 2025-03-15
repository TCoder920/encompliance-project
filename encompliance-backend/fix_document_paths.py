import os
import sys
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Document
from app.core.config import get_settings

settings = get_settings()

def fix_document_paths():
    """
    Check and fix document paths in the database and file system.
    This script will:
    1. Check if each document file exists at the expected path
    2. If not, try to find it in alternative locations
    3. If found, copy it to the correct location
    4. If not found, report the missing file
    """
    # Create DB session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all non-deleted documents
        documents = db.query(Document).filter(Document.is_deleted == False).all()
        print(f"Found {len(documents)} documents to check")
        
        # Ensure the PDF storage directory exists
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Process each document
        for doc in documents:
            print(f"\nChecking document: ID={doc.id}, Filename={doc.filename}, Path={doc.filepath}")
            
            # Check if the file exists at the expected path
            expected_path = os.path.join(settings.PDF_STORAGE_PATH, doc.filepath)
            if os.path.exists(expected_path):
                print(f"✅ File exists at expected path: {expected_path}")
                continue
            
            print(f"❌ File not found at expected path: {expected_path}")
            
            # Try alternative paths
            alternative_paths = [
                # Try with just the filename (no timestamp)
                os.path.join(settings.PDF_STORAGE_PATH, doc.filename),
                
                # Try in the resources directory
                os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "resources", doc.filename),
                
                # Try in the pdf_storage directory
                os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "pdf_storage", doc.filepath),
                
                # Try with just the filename in pdf_storage
                os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "pdf_storage", doc.filename)
            ]
            
            found = False
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    print(f"✅ Found file at alternative path: {alt_path}")
                    
                    # Copy the file to the expected path
                    print(f"📋 Copying file from {alt_path} to {expected_path}")
                    shutil.copy2(alt_path, expected_path)
                    
                    print(f"✅ File copied successfully")
                    found = True
                    break
            
            if not found:
                print(f"❌ File not found at any alternative path")
                
                # Check if we have a default file for common documents
                if doc.filename == "chapter-746-centers.pdf":
                    default_path = os.path.join(settings.PDF_STORAGE_PATH, "chapter-746-centers.pdf")
                    if os.path.exists(default_path):
                        print(f"✅ Found default file for {doc.filename}")
                        
                        # Copy the default file to the expected path
                        print(f"📋 Copying default file to {expected_path}")
                        shutil.copy2(default_path, expected_path)
                        
                        print(f"✅ Default file copied successfully")
                    else:
                        print(f"❌ Default file not found for {doc.filename}")
                elif doc.filename == "test.pdf":
                    # Try to find any test.pdf or test_compliance.pdf file
                    test_files = []
                    for root, dirs, files in os.walk(os.path.dirname(settings.PDF_STORAGE_PATH)):
                        for file in files:
                            if file.endswith(".pdf") and ("test" in file.lower() or "compliance" in file.lower()):
                                test_files.append(os.path.join(root, file))
                    
                    if test_files:
                        print(f"✅ Found {len(test_files)} test PDF files")
                        test_path = test_files[0]
                        
                        # Copy the test file to the expected path
                        print(f"📋 Copying test file from {test_path} to {expected_path}")
                        shutil.copy2(test_path, expected_path)
                        
                        print(f"✅ Test file copied successfully")
                    else:
                        print(f"❌ No test PDF files found")
        
        print("\nDocument path check and fix completed")
        
    except Exception as e:
        print(f"Error fixing document paths: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    fix_document_paths() 