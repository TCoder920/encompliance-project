# Encompliance.io - AI-Powered Compliance Assistant

This application provides an AI-powered compliance assistant for Texas daycare and GRO (General Residential Operation) facilities.

## Features

- Interactive document viewer for Texas Health and Human Services regulations
- AI-powered chat assistant for compliance questions
- Document upload functionality for custom compliance documents
- User dashboard for tracking compliance activities

## AI Integration

The application supports integration with real AI models through the OpenAI API. To enable this feature:

1. Create a `.env` file in the root directory (copy from `.env.example`)
2. Add your OpenAI API key:
   ```
   VITE_OPENAI_API_KEY=your_openai_api_key_here
   ```

Without an API key, the application will run in "Demo Mode" with pre-programmed responses.

## Available AI Models

The application supports multiple AI models:

- **Llama 3 8B**: Efficient model suitable for fast responses to general compliance questions  
- **GPT-4o-mini**: Compact and capable model optimized for complex compliance questions
- **Demo Mode**: Pre-programmed responses (no API key required)

## Development

To run the application locally:

```bash
npm install
npm run dev
```

## Security Note

In a production environment, API calls to OpenAI should be proxied through a backend service to protect your API key. The current implementation with `dangerouslyAllowBrowser: true` is for demonstration purposes only.