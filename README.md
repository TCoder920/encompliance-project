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

## Environment Variables

The application requires several environment variables to be set for proper operation. A template `.env.example` file is provided at the root of the repository. Copy this file to `.env` and update the values as needed.

**Important**: Never commit `.env` files to the repository. They contain sensitive information such as API keys and database credentials.

### Required Environment Variables

- **Database Configuration**:
  - `DB_USER`: PostgreSQL username
  - `DB_PASSWORD`: PostgreSQL password
  - `DB_NAME`: PostgreSQL database name

- **Security**:
  - `JWT_SECRET_KEY`: Secret key for JWT token generation
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time in minutes
  - `ENCRYPTION_KEY`: Key used for encrypting API keys in the database

- **Frontend Configuration**:
  - `FRONTEND_PORT`: Port for the frontend server
  - `FRONTEND_URL`: URL for the frontend server

- **Backend Configuration**:
  - `BACKEND_PORT`: Port for the backend server

## Running the Application

### Development Mode

To run the complete application in development mode:

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

### Production Mode

For production deployment, Docker is recommended:

```bash
# Build and start the containers
docker compose up -d

# Stop the containers
docker compose down
```

## License

MIT License 