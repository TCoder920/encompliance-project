# Retrieval-Augmented Generation (RAG) System

This document explains the Retrieval-Augmented Generation (RAG) system implemented in the Encompliance application to enhance AI responses with information from PDF documents.

## Overview

The RAG system allows the AI assistant to reference information from uploaded PDF documents when answering user queries. This enables more accurate and specific responses related to compliance regulations and requirements.

## Components

The RAG system consists of the following components:

1. **PDF Storage**: PDFs are uploaded through the frontend and stored in a designated directory on the server.

2. **PDF Database Records**: Information about each PDF (filename, path, uploader, etc.) is stored in the database.

3. **PDF Text Extraction**: When a query references a PDF, the system extracts text from the PDF using PyPDF2.

4. **Context Enhancement**: The extracted text is added to the system message sent to the LLM, providing context for the user's query.

5. **Chat Interface**: The frontend allows users to select PDFs to include in their queries.

## Implementation Details

### PDF Service

The `pdf_service.py` file contains functions for:
- Extracting text from PDFs (`extract_text_from_pdf`)
- Getting context from multiple PDFs (`get_pdf_context`)
- Listing, downloading, and deleting PDFs

### Chat Utilities

The `chat_utils.py` file contains utilities for:
- Enhancing system messages with PDF context
- Formatting chat history for the LLM
- Generating compliance-specific system messages

### LLM Service

The `llm_service.py` file has been updated to:
- Accept PDF IDs and database sessions
- Retrieve PDF context when needed
- Format messages with PDF context for different LLM providers

### Chat API

The chat endpoint in `chat.py` has been updated to:
- Accept PDF IDs in the request
- Pass the database session to the LLM service
- Log queries with associated PDF information

## Testing

Several test scripts have been created to verify the PDF functionality:

1. `test_pdf_context.py`: Creates a test PDF and verifies text extraction
2. `test_pdf_extraction.py`: Simplified script for testing PDF extraction

## Usage

To use the RAG system:

1. Upload PDFs through the frontend interface
2. When asking a question, select relevant PDFs from the sidebar
3. Submit your query, and the AI will include information from the selected PDFs in its response

## Example

When a user asks "What are the staff-to-child ratio requirements?" and selects a PDF containing regulations, the system will:

1. Extract text from the selected PDF
2. Add this text to the system message sent to the LLM
3. The LLM will reference the specific regulations from the PDF in its response
4. The response will cite the source document when providing information

## Future Improvements

Potential enhancements to the RAG system:

1. **Chunking**: Split large PDFs into smaller chunks for more efficient processing
2. **Embedding**: Generate vector embeddings for PDF chunks for semantic search
3. **Relevance Ranking**: Rank PDF chunks by relevance to the query
4. **Multi-document Reasoning**: Improve the system's ability to reason across multiple documents
5. **OCR Integration**: Add OCR capabilities for scanned documents 