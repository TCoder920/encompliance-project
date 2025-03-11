# Encompliance.io Backend

This is the FastAPI backend for the Encompliance.io compliance platform.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file and add your API keys.

## Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000.

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Available Endpoints

- `POST /api/v1/chat`: Process a chat request and return a response from the LLM.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `DEFAULT_MODEL`: The default LLM model to use 