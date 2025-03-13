import os
import sys
import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        text = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text.append(f"Page {page_num + 1}:\n{page.extract_text()}")
        
        return "\n\n".join(text)
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return f"[Error extracting text from {os.path.basename(pdf_path)}]"

def main():
    """Main function"""
    # Check if a PDF path was provided as an argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Use the test PDF created by test_pdf_context.py
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")
        pdf_path = os.path.join(resources_dir, "test_compliance.pdf")
    
    # Check if the PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    print(f"Extracting text from PDF: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Print the extracted text
    if text:
        print(f"\nSuccessfully extracted text ({len(text)} characters)")
        print("\nText preview:")
        print(text[:1000] + "..." if len(text) > 1000 else text)
    else:
        print("Failed to extract text")

if __name__ == "__main__":
    main() 