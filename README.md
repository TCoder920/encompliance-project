# Encompliance.io

A comprehensive compliance management platform designed for healthcare facilities to streamline regulatory compliance processes.

## Overview

Encompliance.io provides an end-to-end solution for healthcare facilities to manage their compliance documentation, track regulatory requirements, and ensure adherence to industry standards. The platform offers document management, compliance tracking, and reporting capabilities in a secure, user-friendly interface.

## Key Features

- **Document Management**: Secure storage and organization of compliance-related documents
- **Regulatory Tracking**: Monitor compliance status across multiple regulatory frameworks
- **Automated Notifications**: Receive alerts for upcoming deadlines and compliance gaps
- **Comprehensive Reporting**: Generate detailed compliance reports for audits and internal reviews
- **User Role Management**: Granular access controls based on organizational roles

## Project Architecture

The application follows a modern microservices architecture:

- **Frontend**: React-based single-page application with responsive design
- **Backend**: FastAPI-based REST API with PostgreSQL database
- **Document Storage**: Secure document repository with encryption and access controls

## Security Features

- JWT-based authentication
- Role-based access control
- Encrypted storage of sensitive information
- Comprehensive audit logging
- HTTPS enforcement

## Environment Configuration

The application requires environment variables for proper operation. A template `.env.example` file is provided at the root of the repository. Copy this file to `.env` and update the values accordingly.

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

## Deployment

### Development Environment

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

### Production Deployment

For production deployment, Docker is recommended:

```bash
# Build and start the containers
docker compose up -d

# Stop the containers
docker compose down
```

## License

Proprietary and Confidential. © 2025 Encompliance.io. All rights reserved. 