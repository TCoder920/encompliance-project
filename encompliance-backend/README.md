# Encompliance.io Backend

This is the backend API for Encompliance.io, an AI-powered compliance assistant for Texas daycare and GRO (General Residential Operation) facilities.

## Features

- User authentication with JWT (with AWS Cognito integration option)
- PDF document storage and retrieval (AWS S3 or MinIO)
- AI chatbot integration with Llama 3 8B Instruct model
- Stripe payment processing for subscriptions and one-time payments
- User profile management

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with optional AWS Cognito integration
- **Storage**: AWS S3 with MinIO fallback
- **AI Integration**: Llama 3 8B Instruct model or OpenAI
- **Payments**: Stripe API
- **Containerization**: Docker
- **Infrastructure**: AWS (ECS, RDS, S3, etc.)

## Project Structure

```
encompliance-backend/
├── app/                    # Application code
│   ├── api/                # API endpoints
│   │   ├── auth/           # Authentication endpoints
│   │   ├── chat/           # AI chat endpoints
│   │   ├── pdfs/           # PDF storage endpoints
│   │   ├── payments/       # Stripe payment endpoints
│   │   └── users/          # User management endpoints
│   ├── core/               # Core application code
│   │   ├── config.py       # Application configuration
│   │   └── security.py     # Security utilities
│   ├── db/                 # Database setup
│   │   ├── base.py         # Base models
│   │   └── session.py      # Database session
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # External services
│   │   ├── ai_service.py   # AI model integration
│   │   ├── s3.py           # S3/MinIO integration
│   │   └── stripe_service.py # Stripe integration
│   ├── utils/              # Utilities
│   └── main.py             # FastAPI application
├── deployment/             # Deployment configuration
│   └── terraform/          # Terraform IaC
├── scripts/                # Utility scripts
├── .env.example            # Example environment variables
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- MinIO (for local development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/encompliance-backend.git
   cd encompliance-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your configuration.

### Running with Docker

```bash
docker-compose up -d
```

This will start the FastAPI application, PostgreSQL database, and MinIO storage.

### Running without Docker

1. Start a PostgreSQL database.
2. Start a MinIO server or configure AWS S3.
3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Environment Variables

See `.env.example` for a list of required environment variables.

## Deployment

### AWS Deployment

The application is designed to be deployed on AWS using the following services:

- ECS (Fargate) for containerized application
- RDS for PostgreSQL database
- S3 for file storage
- Cognito for authentication (optional)
- API Gateway for API management

Terraform configurations are provided in the `deployment/terraform` directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
