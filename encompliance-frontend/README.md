# Encompliance.io - AI-Powered Compliance Assistant

This application provides an AI-powered compliance assistant for Texas daycare and GRO (General Residential Operation) facilities.

## Features

- Interactive document viewer for Texas Health and Human Services regulations
- AI-powered chat assistant for compliance questions
- Document upload functionality for custom compliance documents
- User dashboard for tracking compliance activities

## Document Storage

All documents (PDFs) uploaded through the application are stored in the `encompliance-documents` directory at the root of the project. The frontend communicates with the backend API to upload, retrieve, and manage these documents.

Document metadata (filename, upload date, etc.) is stored in the PostgreSQL database, but the actual files are stored in the `encompliance-documents` directory with timestamped filenames to prevent collisions.

## AI Integration

The application integrates with AI models through the OpenAI API. To enable this feature:

1. Create a `.env` file in the root directory (copy from `.env.example`)
2. Add your OpenAI API key:
   ```
   VITE_OPENAI_API_KEY=your_openai_api_key_here
   ```

## Available AI Models

The application supports multiple AI models:

- **Local LLM**: A locally hosted model running on http://127.0.0.1:1234 for fast responses to compliance questions
- **GPT-4o-mini**: Compact and capable model optimized for complex compliance questions

## Development

To run the application locally:

```bash
npm install
npm run dev
```

## Security Note

In a production environment, API calls to OpenAI should be proxied through a backend service to protect your API key.