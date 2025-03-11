# Encompliance.io Backend

This is the backend API for the Encompliance.io compliance platform.

## Features

- FastAPI-based REST API
- PostgreSQL database for user authentication
- JWT-based authentication
- Local LLM integration
- PDF document processing

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- LM Studio (for local model support)

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

4. Set up the PostgreSQL database:
```bash
# Create a new PostgreSQL database
createdb encompliance
```

5. Configure environment variables:
   - Copy the `.env.example` file to `.env`
   - Update the values in the `.env` file with your configuration

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

The API uses JWT-based authentication. To access protected endpoints:

1. Register a new user:
```bash
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "testuser", "password": "password123"}'
```

2. Login to get a JWT token:
```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

3. Use the token to access protected endpoints:
```bash
curl -X GET http://localhost:8000/api/v1/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Local Model Integration

To use a local LLM model:

1. Start LM Studio and load your model
2. Set the following environment variables in your `.env` file:
```
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:1234
LOCAL_MODEL_NAME=your_model_name
```

## License

[MIT License](LICENSE) 