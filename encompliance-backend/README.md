# Encompliance.io Backend

This is the backend API for Encompliance.io, a modular, secure, and local-first compliance platform.

## Features

- User authentication with JWT tokens
- Role-based access control
- PDF storage and retrieval
- AI chatbot integration (local or placeholder)
- PostgreSQL database integration

## Requirements

- Python 3.10+
- PostgreSQL
- Docker (optional)

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/encompliance-backend.git
cd encompliance-backend
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up the database:
```bash
# Make sure PostgreSQL is running
python -m app.db.init_db_script
```

5. Run the application:
```bash
uvicorn main:app --reload
```

### Docker Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/encompliance-backend.git
cd encompliance-backend
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the Docker containers:
```bash
docker-compose up -d
```

4. Initialize the database:
```bash
docker-compose exec api python -m app.db.init_db_script
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
encompliance-backend/
├── app/                    # Application package
│   ├── api/                # API endpoints
│   │   └── api_v1/         # API version 1
│   │       └── endpoints/  # API endpoint modules
│   ├── core/               # Core modules
│   ├── crud/               # CRUD operations
│   ├── db/                 # Database setup
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── storage/                # Local storage for PDFs
│   └── pdfs/               # PDF storage directory
├── tests/                  # Test modules
├── .env                    # Environment variables
├── .env.example            # Example environment variables
├── Dockerfile              # Dockerfile for containerization
├── docker-compose.yml      # Docker Compose configuration
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

## License

[MIT License](LICENSE) 