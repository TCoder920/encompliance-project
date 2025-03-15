# Updates - March 13, 2023

## Changes Made

1. **Fixed Operation Type Selection Process**
   - Fixed the signup flow to properly redirect to the operation type selection page after successful signup
   - Users will now be prompted to select between "Daycare" or "GRO/RTC" after registration
   - This ensures proper content is shown based on user's operation type

2. **Fixed PDF Document Loading**
   - Added missing "chapter-748-gro.pdf" for GRO/RTC operation type
   - Created a download script to ensure all required PDFs are available
   - PDF files are now properly loaded in the document viewer

3. **Added Download Script**
   - Created `download_standard_pdfs.py` to download standard PDF files
   - This ensures all required documents are available in the system
   - Run this script if you encounter missing document errors

## How to Run the Download Script

```bash
# From the encompliance-backend directory
python download_standard_pdfs.py
```

The script will download any missing PDF files required by the application.

## Next Steps

If you encounter any other issues, please let us know. 