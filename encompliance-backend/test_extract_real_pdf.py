import os
import PyPDF2
import traceback
from app.core.config import get_settings

settings = get_settings()

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        text = []
        
        print(f"Attempting to extract text from PDF: {pdf_path}")
        print(f"File exists: {os.path.exists(pdf_path)}")
        print(f"File size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
        
        # First, verify the file is a valid PDF
        try:
            with open(pdf_path, 'rb') as file:
                # Check if file starts with PDF signature
                header = file.read(5)
                print(f"File header: {header}")
                if header != b'%PDF-':
                    print(f"WARNING: File does not appear to be a valid PDF (header: {header})")
                    return f"[Error: File does not appear to be a valid PDF]"
        except Exception as e:
            print(f"Error checking PDF header: {str(e)}")
            return f"[Error checking PDF header: {str(e)}]"
        
        # Now try to extract text
        with open(pdf_path, 'rb') as file:
            try:
                # Use a try-except block for creating the reader
                try:
                    reader = PyPDF2.PdfReader(file, strict=False)
                    print(f"Successfully created PDF reader")
                except Exception as reader_error:
                    print(f"Error creating PDF reader: {str(reader_error)}")
                    print(f"Traceback: {traceback.format_exc()}")
                    return f"[Error reading PDF {os.path.basename(pdf_path)}: {str(reader_error)}]"
                
                # Get number of pages
                try:
                    num_pages = len(reader.pages)
                    print(f"PDF has {num_pages} pages")
                except Exception as page_error:
                    print(f"Error getting page count: {str(page_error)}")
                    return f"[Error getting page count: {str(page_error)}]"
                
                # Extract text from each page
                for page_num in range(num_pages):
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text:
                            text.append(f"[Page {page_num + 1}]\n{page_text}")
                            print(f"Successfully extracted text from page {page_num + 1} ({len(page_text)} characters)")
                        else:
                            text.append(f"[Page {page_num + 1} - No text content]")
                            print(f"No text content found on page {page_num + 1}")
                    except Exception as page_error:
                        print(f"Error extracting text from page {page_num + 1}: {str(page_error)}")
                        text.append(f"[Page {page_num + 1} - Error: {str(page_error)}]")
            except Exception as reader_error:
                print(f"Error creating PDF reader: {str(reader_error)}")
                return f"[Error reading PDF {os.path.basename(pdf_path)}: {str(reader_error)}]"
        
        # If we extracted no text at all, return an error
        if not text:
            return f"[No text could be extracted from {os.path.basename(pdf_path)}]"
            
        result = "\n\n".join(text)
        print(f"Total extracted text: {len(result)} characters")
        return result
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return f"[Error extracting text from {os.path.basename(pdf_path)}: {str(e)}]"

def main():
    # Path to the real test.pdf file
    pdf_path = "/Users/midnight/Documents/encompliance-project/encompliance-backend/encompliance-documents/20250314223911_real test.pdf"
    
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Print the extracted text
    print("\n" + "="*50 + "\n")
    print("EXTRACTED TEXT:")
    print(text)

if __name__ == "__main__":
    main() 