# Encompliance.io Project

This is the main repository for the Encompliance.io compliance platform.

## Project Structure

The project consists of three main components:

- **encompliance-frontend**: React-based web application
- **encompliance-backend**: FastAPI-based REST API
- **encompliance-documents**: Document storage directory

## Document Storage

All documents (PDFs) are stored in the `encompliance-documents` directory at the root of the project. This location is hardcoded in the application settings and cannot be changed.

### Document Metadata

While the actual document files are stored in the `encompliance-documents` directory, the document metadata (filename, upload date, owner, etc.) is stored in the PostgreSQL database in the `pdfs` table.

### Document File Format

Documents are stored with timestamped filenames to prevent collisions, using the format:
```
YYYYMMDDHHMMSS_original_filename.pdf
```

For example:
```
20250313035653_chapter-746-centers.pdf
```

## Setup Instructions

See the README files in the respective directories:
- [Frontend README](encompliance-frontend/README.md)
- [Backend README](encompliance-backend/README.md)

## Running the Application

To run the complete application:

1. Start the backend:
```bash
cd encompliance-backend
python -m uvicorn app.main:app --reload
```

2. Start the frontend:
```bash
cd encompliance-frontend
npm run dev
```

## License

MIT License 