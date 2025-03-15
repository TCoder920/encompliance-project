import os
import requests
import sys

# PDF URLs - these are example URLs, replace with actual URLs if different
PDFS = {
    "chapter-746-centers.pdf": "https://www.hhs.texas.gov/sites/default/files/documents/doing-business-with-hhs/provider-portal/protective-services/ccl/min-standards/chapter-746-centers.pdf",
    "chapter-748-gro.pdf": "https://www.hhs.texas.gov/sites/default/files/documents/doing-business-with-hhs/provider-portal/protective-services/ccl/min-standards/chapter-748-gro.pdf"
}

def download_pdf(url, filename, directory):
    """Download a PDF file from a URL and save it to the specified directory."""
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Save the file
        filepath = os.path.join(directory, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded {filename} successfully to {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def main():
    # Default directory
    pdf_directory = "encompliance-documents"
    
    # Check if a directory is provided as an argument
    if len(sys.argv) > 1:
        pdf_directory = sys.argv[1]
    
    print(f"Using directory: {pdf_directory}")
    
    # Track success
    success_count = 0
    
    # Download each PDF
    for filename, url in PDFS.items():
        filepath = os.path.join(pdf_directory, filename)
        
        # Check if file exists but is empty or corrupt
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"{filename} already exists, skipping download.")
            success_count += 1
        else:
            print(f"{filename} is missing or corrupt, re-downloading...")
            if download_pdf(url, filename, pdf_directory):
                success_count += 1
    
    # Print summary
    print(f"\nDownloaded {success_count} of {len(PDFS)} files to {pdf_directory}")
    
    if success_count < len(PDFS):
        print("Some files failed to download. Please check the logs above.")
        return 1
    else:
        print("All files downloaded successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 