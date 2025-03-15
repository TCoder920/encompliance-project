import os
import sys
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "password123"
}

def create_test_user():
    """Create a test user if it doesn't exist."""
    try:
        # Check if user exists by trying to log in
        response = requests.post(
            f"{BASE_URL}/email-login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
        )
        
        if response.status_code == 200:
            print(f"Test user {TEST_USER['email']} already exists.")
            return response.json()["access_token"]
        
        # Create user if login fails
        response = requests.post(
            f"{BASE_URL}/signup",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "full_name": "Test User",
                "operation_name": "Test Operation"
            }
        )
        
        if response.status_code == 201:
            print(f"Created test user: {TEST_USER['email']}")
            
            # Log in to get token
            response = requests.post(
                f"{BASE_URL}/email-login",
                json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
            )
            
            return response.json()["access_token"]
        else:
            print(f"Failed to create test user: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        return None

def test_document_upload(token, file_path):
    """Test uploading a document."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        # Get file name and extension
        file_name = os.path.basename(file_path)
        
        # Upload file
        with open(file_path, "rb") as file:
            response = requests.post(
                f"{BASE_URL}/documents/upload",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (file_name, file)}
            )
        
        if response.status_code == 201:
            document = response.json()
            print(f"Uploaded document: {document['filename']}")
            print(f"Document ID: {document['id']}")
            print(f"Document Type: {document['file_type']}")
            print(f"Document Size: {document['file_size']} bytes")
            return document
        else:
            print(f"Failed to upload document: {response.text}")
            return None
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        return None

def test_document_list(token):
    """Test listing documents."""
    try:
        response = requests.get(
            f"{BASE_URL}/documents/list",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            documents = response.json()["documents"]
            print(f"Found {len(documents)} documents:")
            for doc in documents:
                print(f"  - ID: {doc['id']}, Name: {doc['filename']}, Type: {doc['file_type']}, Size: {doc['file_size']} bytes")
            return documents
        else:
            print(f"Failed to list documents: {response.text}")
            return None
    except Exception as e:
        print(f"Error listing documents: {str(e)}")
        return None

def test_document_download(token, document_id):
    """Test downloading a document."""
    try:
        response = requests.get(
            f"{BASE_URL}/documents/download/{document_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            # Get filename from content-disposition header
            content_disposition = response.headers.get("content-disposition", "")
            filename = content_disposition.split("filename=")[1].strip('"') if "filename=" in content_disposition else f"document_{document_id}"
            
            # Save file
            download_path = f"downloaded_{filename}"
            with open(download_path, "wb") as file:
                file.write(response.content)
            
            print(f"Downloaded document to: {download_path}")
            return download_path
        else:
            print(f"Failed to download document: {response.text}")
            return None
    except Exception as e:
        print(f"Error downloading document: {str(e)}")
        return None

def test_document_delete(token, document_id):
    """Test deleting a document."""
    try:
        response = requests.delete(
            f"{BASE_URL}/documents/delete/{document_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            document = response.json()
            print(f"Deleted document: {document['filename']}")
            print(f"Deleted at: {document['deleted_at']}")
            return document
        else:
            print(f"Failed to delete document: {response.text}")
            return None
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return None

def main():
    """Main test function."""
    # Create test user and get token
    token = create_test_user()
    if not token:
        print("Failed to get authentication token. Exiting.")
        return
    
    print("\n=== Testing Document Upload ===")
    # Test uploading a PDF
    pdf_path = "resources/test.pdf"
    if not os.path.exists(pdf_path):
        # Create a simple test PDF if it doesn't exist
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas("resources/test.pdf")
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 700, "Created for testing document handling")
            c.drawString(100, 650, f"Created at: {datetime.now().isoformat()}")
            c.save()
            print(f"Created test PDF at {pdf_path}")
        except Exception as e:
            print(f"Failed to create test PDF: {str(e)}")
            pdf_path = None
    
    if pdf_path:
        pdf_doc = test_document_upload(token, pdf_path)
    
    # Test uploading a text file
    txt_path = "resources/test.txt"
    if not os.path.exists(txt_path):
        # Create a simple test text file if it doesn't exist
        try:
            os.makedirs("resources", exist_ok=True)
            with open(txt_path, "w") as f:
                f.write("Test Text Document\n")
                f.write("Created for testing document handling\n")
                f.write(f"Created at: {datetime.now().isoformat()}\n")
            print(f"Created test text file at {txt_path}")
        except Exception as e:
            print(f"Failed to create test text file: {str(e)}")
            txt_path = None
    
    if txt_path:
        txt_doc = test_document_upload(token, txt_path)
    
    print("\n=== Testing Document List ===")
    documents = test_document_list(token)
    
    if documents and len(documents) > 0:
        doc_id = documents[0]["id"]
        
        print(f"\n=== Testing Document Download (ID: {doc_id}) ===")
        download_path = test_document_download(token, doc_id)
        
        print(f"\n=== Testing Document Delete (ID: {doc_id}) ===")
        test_document_delete(token, doc_id)
        
        print("\n=== Verifying Document List After Deletion ===")
        test_document_list(token)

if __name__ == "__main__":
    main() 