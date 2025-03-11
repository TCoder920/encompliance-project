import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class PDFService:
    def __init__(self):
        self.storage_path = Path(settings.PDF_STORAGE_PATH)
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def save_pdf(self, file: UploadFile, state: str, category: str) -> str:
        """
        Save a PDF file to the storage directory
        
        Args:
            file: The uploaded PDF file
            state: The state code (e.g., 'TX')
            category: The document category
            
        Returns:
            The file path relative to the storage directory
        """
        # Generate a unique filename to avoid collisions
        unique_filename = f"{uuid4().hex}_{file.filename}"
        
        # Create state and category subdirectories if they don't exist
        state_dir = self.storage_path / state.lower()
        category_dir = state_dir / category.lower()
        state_dir.mkdir(exist_ok=True)
        category_dir.mkdir(exist_ok=True)
        
        # Full path to save the file
        file_path = category_dir / unique_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return the relative path from the storage root
        return str(file_path.relative_to(self.storage_path))
    
    def get_pdf_path(self, relative_path: str) -> Path:
        """
        Get the full path to a PDF file
        
        Args:
            relative_path: The path relative to the storage directory
            
        Returns:
            The full path to the PDF file
        """
        return self.storage_path / relative_path
    
    def delete_pdf(self, relative_path: str) -> bool:
        """
        Delete a PDF file
        
        Args:
            relative_path: The path relative to the storage directory
            
        Returns:
            True if the file was deleted, False otherwise
        """
        full_path = self.get_pdf_path(relative_path)
        
        if full_path.exists():
            os.remove(full_path)
            return True
        
        return False


# Create a singleton instance
pdf_service = PDFService() 