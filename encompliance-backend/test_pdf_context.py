import os
import PyPDF2
import traceback
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def create_test_pdf(output_path):
    """Create a test PDF file"""
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"Created test PDF at: {output_path}")
    return output_path

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
        print(traceback.format_exc())
        return f"[Error extracting text from {os.path.basename(pdf_path)}]"

def test_pdf_extraction():
    """Test the PDF extraction functionality"""
    # Create resources directory if it doesn't exist
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create test PDF
    test_pdf_path = os.path.join(resources_dir, "test_compliance.pdf")
    if not os.path.exists(test_pdf_path):
        test_pdf_path = create_test_pdf(test_pdf_path)
    
    print(f"\nTesting PDF at path: {test_pdf_path}")
    print(f"File exists: {os.path.exists(test_pdf_path)}")
    print(f"File size: {os.path.getsize(test_pdf_path)} bytes")
    
    # Extract text from PDF
    print("\nExtracting text from PDF...")
    text = extract_text_from_pdf(test_pdf_path)
    
    # Print extracted text
    if text:
        print(f"\nSuccessfully extracted text ({len(text)} characters)")
        print("Text preview:")
        print(text[:500] + "..." if len(text) > 500 else text)
    else:
        print("Failed to extract text")

if __name__ == "__main__":
    test_pdf_extraction()