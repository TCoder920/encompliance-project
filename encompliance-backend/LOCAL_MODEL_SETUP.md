# Setting Up Local LLM Models with Encompliance.io

This guide explains how to set up and use local LLM models with the Encompliance.io platform.

## Supported Local Model Servers

The backend is designed to work with the following local model servers:

1. **LM Studio** - A GUI for running local LLMs (https://lmstudio.ai/)
2. **Any OpenAI API-compatible server** - Any server that implements the OpenAI API format

## Setting Up LM Studio

1. **Install LM Studio**:
   - Download and install from https://lmstudio.ai/

2. **Load a model in LM Studio**

3. **Start the local server**:
   - In LM Studio, click on "Local Server" and start the server

4. **Configure Encompliance.io**:
   - Edit the `.env` file in the `encompliance-backend` directory:
     ```
     USE_LOCAL_MODEL=true
     LOCAL_MODEL_URL=http://localhost:1234/v1
     LOCAL_MODEL_NAME=local-model
     ```
   - Replace `1234` with the port your LM Studio server is running on
   - The `LOCAL_MODEL_NAME` should be set to "local-model"

## Using the Local Model

1. **Start the backend server**:
   ```bash
   cd encompliance-backend
   source venv/bin/activate
   python run.py
   ```

2. **In the frontend**:
   - Open the chat interface
   - Click on the settings icon
   - Select "Local LLM" from the model selector

## Troubleshooting

If you encounter issues with the local model:

1. **Check the model server**:
   - Make sure your local model server is running
   - Verify the URL and port in the `.env` file

2. **Test the local model API**:
   ```bash
   cd encompliance-backend
   source venv/bin/activate
   python test_local_model.py
   ```

3. **Check the logs**:
   - Look for error messages in the backend server logs

4. **Alternative model setup**:
   - If the local model service is unavailable, the system will use OpenAI if configured
   - If you want to use OpenAI models, set `USE_LOCAL_MODEL=false` and provide an OpenAI API key 