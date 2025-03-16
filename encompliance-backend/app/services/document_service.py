import os
import PyPDF2
import traceback
import mimetypes
import shutil
import re
import json
import hashlib
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from app.core.config import get_settings
from app.models.document import Document
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.models.user import User
from datetime import datetime

settings = get_settings()

# Directory to store document indexes
INDEX_DIR = os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "document_indexes")
os.makedirs(INDEX_DIR, exist_ok=True)

# Directory to store document embeddings
EMBEDDING_DIR = os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "document_embeddings")
os.makedirs(EMBEDDING_DIR, exist_ok=True)

# Flag to control whether to use embeddings (can be disabled if dependencies aren't installed)
USE_EMBEDDINGS = True

try:
    from sentence_transformers import SentenceTransformer
    # Load the embedding model (this will be lazy-loaded when needed)
    _embedding_model = None
    
    def get_embedding_model():
        """Get or initialize the embedding model"""
        global _embedding_model
        if _embedding_model is None:
            try:
                # Use a smaller, faster model for production
                _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Loaded embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                print(f"Error loading embedding model: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                global USE_EMBEDDINGS
                USE_EMBEDDINGS = False
        return _embedding_model
    
    def compute_embeddings(texts: List[str]) -> np.ndarray:
        """Compute embeddings for a list of texts"""
        if not USE_EMBEDDINGS:
            return None
        
        try:
            model = get_embedding_model()
            embeddings = model.encode(texts)
            return embeddings
        except Exception as e:
            print(f"Error computing embeddings: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return None
    
    def compute_similarity(query_embedding: np.ndarray, chunk_embeddings: np.ndarray) -> List[float]:
        """Compute cosine similarity between query and chunks"""
        # Normalize the embeddings for cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        chunk_norms = chunk_embeddings / np.linalg.norm(chunk_embeddings, axis=1, keepdims=True)
        
        # Compute cosine similarity
        similarities = np.dot(chunk_norms, query_norm)
        return similarities.tolist()
        
except ImportError:
    print("Warning: sentence-transformers not installed. Falling back to keyword matching.")
    USE_EMBEDDINGS = False
    
    def get_embedding_model():
        return None
    
    def compute_embeddings(texts: List[str]) -> None:
        return None
    
    def compute_similarity(query_embedding, chunk_embeddings) -> List[float]:
        return []

def get_document_index_path(doc_id: int) -> str:
    """Get the path to the document index file"""
    return os.path.join(INDEX_DIR, f"doc_{doc_id}_index.json")

def get_document_embedding_path(doc_id: int) -> str:
    """Get the path to the document embeddings file"""
    return os.path.join(EMBEDDING_DIR, f"doc_{doc_id}_embeddings.npz")

def create_document_index(doc_id: int, content: str, title: str, chapters: str, headings: str) -> bool:
    """
    Create an index for a document by chunking its content and storing it with metadata.
    
    Args:
        doc_id: Document ID
        content: Document content
        title: Document title
        chapters: Document chapters
        headings: Document headings
        
    Returns:
        True if indexing was successful, False otherwise
    """
    try:
        print(f"Creating index for document ID {doc_id}")
        
        # Create chunks of the document content
        chunks = []
        paragraphs = re.split(r'\n\s*\n', content)
        
        # Group paragraphs into chunks of approximately 5000 characters
        current_chunk = ""
        chunk_size = 5000
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    # Create a hash for the chunk content for future reference
                    chunk_hash = hashlib.md5(current_chunk.encode()).hexdigest()
                    chunks.append({
                        "content": current_chunk.strip(),
                        "hash": chunk_hash,
                        "length": len(current_chunk)
                    })
                current_chunk = para + "\n\n"
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunk_hash = hashlib.md5(current_chunk.encode()).hexdigest()
            chunks.append({
                "content": current_chunk.strip(),
                "hash": chunk_hash,
                "length": len(current_chunk)
            })
        
        # Create the index data structure
        index_data = {
            "doc_id": doc_id,
            "title": title,
            "chapters": chapters,
            "headings": headings,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "total_length": len(content),
            "indexed_at": datetime.now().isoformat()
        }
        
        # Save the index to a file
        index_path = get_document_index_path(doc_id)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        # Create embeddings for the chunks if embeddings are enabled
        if USE_EMBEDDINGS and len(chunks) > 0:
            try:
                # Extract just the content from each chunk
                chunk_texts = [chunk["content"] for chunk in chunks]
                
                # Compute embeddings
                embeddings = compute_embeddings(chunk_texts)
                
                if embeddings is not None:
                    # Save embeddings to a file
                    embedding_path = get_document_embedding_path(doc_id)
                    np.savez_compressed(embedding_path, embeddings=embeddings)
                    print(f"Created embeddings for document ID {doc_id} with {len(chunks)} chunks")
            except Exception as e:
                print(f"Error creating embeddings for document ID {doc_id}: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                # Continue with the index even if embeddings fail
        
        print(f"Successfully created index for document ID {doc_id} with {len(chunks)} chunks")
        return True
    
    except Exception as e:
        print(f"Error creating index for document ID {doc_id}: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def get_document_from_index(doc_id: int, query: str = None) -> Optional[Dict]:
    """
    Retrieve document content from the index, optionally filtering by query.
    
    Args:
        doc_id: Document ID
        query: Optional search query to filter relevant chunks
        
    Returns:
        Dictionary with document content or None if not found
    """
    try:
        index_path = get_document_index_path(doc_id)
        if not os.path.exists(index_path):
            print(f"No index found for document ID {doc_id}")
            return None
        
        # Load the index
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # If no query, return the full document
        if not query:
            # Reconstruct the full content
            content = "\n\n".join([chunk["content"] for chunk in index_data["chunks"]])
            return {
                "title": index_data["title"],
                "chapters": index_data["chapters"],
                "headings": index_data["headings"],
                "content": content,
                "total_chars": index_data["total_length"]
            }
        
        # Check if we can use embeddings for this query
        embedding_path = get_document_embedding_path(doc_id)
        use_embeddings_for_query = USE_EMBEDDINGS and os.path.exists(embedding_path)
        
        if use_embeddings_for_query:
            try:
                # Load embeddings
                embedding_data = np.load(embedding_path)
                chunk_embeddings = embedding_data['embeddings']
                
                # Compute query embedding
                query_embedding = compute_embeddings([query])[0]
                
                # Compute similarities
                similarities = compute_similarity(query_embedding, chunk_embeddings)
                
                # Create scored chunks with semantic similarity
                scored_chunks = [(index_data["chunks"][i]["content"], similarities[i]) 
                                for i in range(len(similarities))]
                
                # Sort by similarity score (highest first)
                scored_chunks.sort(key=lambda x: x[1], reverse=True)
                
                print(f"Using semantic embeddings for document ID {doc_id}")
                
                # Print top scores for debugging
                for i, (_, score) in enumerate(scored_chunks[:5]):
                    print(f"Chunk {i+1} semantic score: {score:.4f}")
                
                # Hybrid approach: also score with keywords for better results
                keyword_scores = score_chunks_by_keywords(index_data["chunks"], query)
                
                # Combine scores (semantic + keyword)
                hybrid_scored_chunks = []
                for i, (content, sem_score) in enumerate(scored_chunks):
                    # Normalize both scores to 0-1 range and combine
                    keyword_score = keyword_scores[i] / 10.0  # Assuming max keyword score around 10
                    hybrid_score = sem_score * 0.7 + keyword_score * 0.3  # Weight semantic higher
                    hybrid_scored_chunks.append((content, hybrid_score))
                
                # Sort by hybrid score
                hybrid_scored_chunks.sort(key=lambda x: x[1], reverse=True)
                
                # Print hybrid scores for debugging
                print("Top hybrid scores (semantic + keyword):")
                for i, (_, score) in enumerate(hybrid_scored_chunks[:5]):
                    print(f"Chunk {i+1} hybrid score: {score:.4f}")
                
                scored_chunks = hybrid_scored_chunks
                
            except Exception as e:
                print(f"Error using embeddings for document ID {doc_id}: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                # Fall back to keyword matching
                use_embeddings_for_query = False
        
        # If embeddings failed or aren't available, use keyword matching
        if not use_embeddings_for_query:
            print(f"Using keyword matching for document ID {doc_id}")
            # Score chunks based on keyword matching
            keyword_scores = score_chunks_by_keywords(index_data["chunks"], query)
            scored_chunks = [(index_data["chunks"][i]["content"], score) 
                            for i, score in enumerate(keyword_scores)]
            
            # Sort by keyword score
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Take the top chunks
        max_chunks = 5  # Adjust based on testing
        
        # Always include the first chunk (often contains important introductory information)
        first_chunk = index_data["chunks"][0]["content"] if index_data["chunks"] else ""
        if first_chunk and first_chunk not in [c[0] for c in scored_chunks[:max_chunks]]:
            top_chunks = [first_chunk] + [c[0] for c in scored_chunks[:max_chunks-1]]
        else:
            top_chunks = [c[0] for c in scored_chunks[:max_chunks]]
        
        # Format the filtered content
        filtered_content = "\n\n".join([
            f"--- RELEVANT SECTION {i+1} ---\n{chunk}" 
            for i, chunk in enumerate(top_chunks)
        ])
        
        # Add a note about content filtering
        filtered_content += "\n\n[Note: Content has been filtered to show only the most relevant sections based on the query. The full document contains more information.]"
        
        print(f"Retrieved {len(filtered_content)} characters from index for document ID {doc_id} based on query")
        
        return {
            "title": index_data["title"],
            "chapters": index_data["chapters"],
            "headings": index_data["headings"],
            "content": filtered_content,
            "total_chars": len(filtered_content)
        }
    
    except Exception as e:
        print(f"Error retrieving document from index for ID {doc_id}: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def score_chunks_by_keywords(chunks: List[Dict], query: str) -> List[float]:
    """Score chunks based on keyword matching with the query"""
    query_terms = query.lower().split()
    scores = []
    
    for chunk in chunks:
        score = 0
        chunk_content = chunk["content"]
        chunk_lower = chunk_content.lower()
        
        # Score based on term frequency
        for term in query_terms:
            if len(term) > 2:  # Ignore very short terms
                score += chunk_lower.count(term)
        
        # Bonus for terms appearing close together
        for i in range(len(query_terms) - 1):
            if len(query_terms[i]) > 2 and len(query_terms[i+1]) > 2:
                pair = f"{query_terms[i]} {query_terms[i+1]}"
                if pair in chunk_lower:
                    score += 5  # Bonus for adjacent terms
        
        # Bonus for terms appearing in the same paragraph
        for para in chunk_content.split("\n\n"):
            para_lower = para.lower()
            term_count = sum(1 for term in query_terms if len(term) > 2 and term in para_lower)
            if term_count > 1:
                score += term_count * 2  # Bonus for multiple terms in same paragraph
        
        scores.append(score)
    
    return scores

async def get_document_context(doc_ids: List[int], db: Session = Depends(get_db), current_user_id: int = None, query: str = None) -> str:
    """
    Extract text from documents and return it as context for the LLM.
    
    Args:
        doc_ids: List of document IDs to extract text from
        db: Database session
        current_user_id: ID of the current user
        query: Optional search query to filter relevant sections
        
    Returns:
        Extracted text from the documents
    """
    try:
        print(f"Retrieving document context for IDs: {doc_ids}, user_id: {current_user_id}")
        if query:
            print(f"Using query for semantic retrieval: '{query[:100]}...' (truncated)")
        
        # Get document records from database, filtering by user ID if provided
        query_db = db.query(Document).filter(Document.id.in_(doc_ids), Document.is_deleted == False)
        
        # If current_user_id is provided, only return documents that belong to the user
        if current_user_id is not None:
            query_db = query_db.filter(Document.uploaded_by == current_user_id)
            
        documents = query_db.all()
        
        print(f"Found {len(documents)} document records for IDs: {doc_ids}")
        
        if not documents:
            print(f"WARNING: No document records found for IDs: {doc_ids}")
            # Check what documents are available
            all_docs_query = db.query(Document)
            if current_user_id is not None:
                all_docs_query = all_docs_query.filter(Document.uploaded_by == current_user_id)
            all_docs = all_docs_query.all()
            
            print(f"Available documents in database: {len(all_docs)}")
            for doc in all_docs:
                print(f"  - ID: {doc.id}, Filename: {doc.filename}, Type: {doc.file_type}, Path: {doc.filepath}, Deleted: {doc.is_deleted}")
            
            return "[No documents found for the requested IDs]"
        
        # Dictionary to store document contexts
        document_contexts = {}
        
        # Extract text from each document
        for doc in documents:
            print(f"Processing document: ID={doc.id}, Filename={doc.filename}, Type={doc.file_type}, Filepath={doc.filepath}")
            
            # First, try to get document from index if it exists
            if query:
                indexed_doc = get_document_from_index(doc.id, query)
                if indexed_doc:
                    print(f"Retrieved document from index for ID {doc.id}")
                    document_contexts[doc.id] = {
                        'filename': doc.filename,
                        'text': f"TITLE: {indexed_doc['title']}\n\nCHAPTERS:\n{indexed_doc['chapters']}\n\nHEADINGS:\n{indexed_doc['headings']}\n\nCONTENT:\n{indexed_doc['content']}",
                        'length': indexed_doc['total_chars'],
                        'id': doc.id,
                        'title': indexed_doc['title'],
                        'headings': indexed_doc['headings'],
                        'chapters': indexed_doc['chapters'],
                        'content': indexed_doc['content']
                    }
                    continue
            
            # If no index or not using query, proceed with normal extraction
            # IMPORTANT: The filepath in the database is just the filename, not the full path
            # We need to join it with the PDF_STORAGE_PATH to get the full path
            file_path = os.path.join(settings.PDF_STORAGE_PATH, doc.filepath)
            
            print(f"Full file path: {file_path}")
            print(f"File exists: {os.path.exists(file_path)}")
            
            if not os.path.exists(file_path):
                print(f"WARNING: Document file not found at primary path: {file_path}")
                
                # Try multiple alternative paths
                alternative_paths = [
                    # Try just the filename in case the path is wrong
                    os.path.join(settings.PDF_STORAGE_PATH, os.path.basename(doc.filepath)),
                    
                    # Try with the filename directly (no timestamp)
                    os.path.join(settings.PDF_STORAGE_PATH, doc.filename),
                    
                    # Try looking in the resources directory
                    os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "resources", doc.filename),
                    
                    # Try looking in the pdf_storage directory
                    os.path.join(os.path.dirname(settings.PDF_STORAGE_PATH), "pdf_storage", doc.filepath),
                    
                    # Try with spaces replaced by underscores
                    os.path.join(settings.PDF_STORAGE_PATH, doc.filepath.replace(" ", "_")),
                    
                    # Try with URL encoding for spaces
                    os.path.join(settings.PDF_STORAGE_PATH, doc.filepath.replace(" ", "%20"))
                ]
                
                # Print all alternative paths we're going to try
                print(f"Trying {len(alternative_paths)} alternative paths:")
                for i, path in enumerate(alternative_paths):
                    print(f"  {i+1}. {path} (exists: {os.path.exists(path)})")
                
                found_file = False
                for alt_path in alternative_paths:
                    print(f"Trying alternative path: {alt_path}")
                    if os.path.exists(alt_path):
                        print(f"Found file at alternative path: {alt_path}")
                        file_path = alt_path
                        found_file = True
                        break
                
                if not found_file:
                    print(f"File not found at any alternative path")
                    
                    # Last resort: list all files in the directory and look for similar names
                    print(f"Listing all files in {settings.PDF_STORAGE_PATH}:")
                    try:
                        all_files = os.listdir(settings.PDF_STORAGE_PATH)
                        for file in all_files:
                            print(f"  - {file}")
                            
                            # Check if this file might be a match
                            if doc.filename.lower() in file.lower():
                                print(f"Possible match found: {file}")
                                possible_match = os.path.join(settings.PDF_STORAGE_PATH, file)
                                if os.path.isfile(possible_match):
                                    print(f"Using possible match: {possible_match}")
                                    file_path = possible_match
                                    found_file = True
                                    break
                    except Exception as e:
                        print(f"Error listing directory: {str(e)}")
                    
                    if not found_file:
                        document_contexts[doc.id] = {
                            'filename': doc.filename,
                            'text': f"[Document {doc.filename} (ID: {doc.id}) not found at {file_path}]",
                            'length': 0,
                            'id': doc.id,
                            'title': doc.filename,
                            'headings': "",
                            'chapters': "",
                            'content': f"[Document {doc.filename} (ID: {doc.id}) not found at {file_path}]"
                        }
                        continue
            
            # Extract text based on file type
            if doc.file_type.lower() == 'pdf' or doc.filename.lower().endswith('.pdf'):
                try:
                    extracted_data = extract_text_from_pdf(file_path)
                    
                    if isinstance(extracted_data, dict) and "error" in extracted_data:
                        error_msg = extracted_data["error"]
                        print(f"Error extracting text: {error_msg}")
                        document_contexts[doc.id] = {
                            'filename': doc.filename,
                            'text': f"[Error extracting text from {doc.filename}: {error_msg}]",
                            'length': 0,
                            'id': doc.id,
                            'title': doc.filename,
                            'headings': "",
                            'chapters': "",
                            'content': f"[Error extracting text from {doc.filename}: {error_msg}]"
                        }
                    else:
                        # Calculate total length
                        title_text = extracted_data.get("title", doc.filename)
                        chapters_text = extracted_data.get("chapters", "")
                        headings_text = extracted_data.get("headings", "")
                        content_text = extracted_data.get("content", "")
                        
                        # If we have a query and the document is large, perform semantic chunking and retrieval
                        original_content_length = len(content_text)
                        if query and original_content_length > 50000:
                            print(f"Large document detected ({original_content_length} chars). Performing semantic chunking and retrieval.")
                            
                            # Get the most relevant chunks based on the query
                            relevant_chunks = get_relevant_chunks(
                                content_text,
                                query,
                                max_chunks=5,  # Adjust based on testing
                                chunk_size=10000  # Adjust based on testing
                            )
                            
                            # Replace the full content with just the relevant chunks
                            content_text = "\n\n".join([
                                f"--- RELEVANT SECTION {i+1} ---\n{chunk}" 
                                for i, chunk in enumerate(relevant_chunks)
                            ])
                            
                            # Add a note about content filtering
                            content_text += "\n\n[Note: Content has been filtered to show only the most relevant sections based on the query. The full document contains more information.]"
                            
                            print(f"Reduced content size from {original_content_length} to {len(content_text)} characters")
                        
                        total_length = (
                            len(title_text) + 
                            len(chapters_text) + 
                            len(headings_text) + 
                            len(content_text)
                        )
                        
                        # Combine all text for backward compatibility
                        full_text = ""
                        if title_text:
                            full_text += f"TITLE: {title_text}\n\n"
                        if chapters_text:
                            full_text += f"CHAPTERS:\n{chapters_text}\n\n"
                        if headings_text:
                            full_text += f"HEADINGS:\n{headings_text}\n\n"
                        if content_text:
                            full_text += f"CONTENT:\n{content_text}\n"
                        
                        document_contexts[doc.id] = {
                            'filename': doc.filename,
                            'text': full_text,
                            'length': total_length,
                            'id': doc.id,
                            'title': title_text,
                            'headings': headings_text,
                            'chapters': chapters_text,
                            'content': content_text
                        }
                        
                        # Create index for this document if it doesn't exist yet
                        index_path = get_document_index_path(doc.id)
                        if not os.path.exists(index_path) and original_content_length > 10000:
                            print(f"Creating index for document ID {doc.id}")
                            create_document_index(
                                doc.id, 
                                extracted_data.get("content", ""),
                                title_text,
                                chapters_text,
                                headings_text
                            )
                except Exception as e:
                    error_msg = f"Error extracting text from {doc.filename}: {str(e)}"
                    print(error_msg)
                    document_contexts[doc.id] = {
                        'filename': doc.filename,
                        'text': f"[{error_msg}]",
                        'length': 0,
                        'id': doc.id,
                        'title': doc.filename,
                        'headings': "",
                        'chapters': "",
                        'content': f"[{error_msg}]"
                    }
            else:
                # For now, just indicate that text extraction is not supported for this file type
                text = f"[Text extraction not supported for {doc.file_type} files]"
                print(f"Text extraction not supported for {doc.file_type} files")
                document_contexts[doc.id] = {
                    'filename': doc.filename,
                    'text': text,
                    'length': len(text),
                    'id': doc.id,
                    'title': doc.filename,
                    'headings': "",
                    'chapters': "",
                    'content': text
                }
        
        # Convert any string error messages to document objects for consistent handling
        for doc_id in document_contexts:
            if isinstance(document_contexts[doc_id], str):
                # Handle error messages which are strings (backward compatibility)
                document_contexts[doc_id] = {
                    'filename': next((doc.filename for doc in documents if doc.id == doc_id), f"Document ID {doc_id}"),
                    'text': document_contexts[doc_id],
                    'length': len(document_contexts[doc_id]),
                    'id': doc_id,
                    'title': f"Document ID {doc_id}",
                    'headings': "",
                    'chapters': "",
                    'content': document_contexts[doc_id]
                }
        
        # Sort document objects by length (shorter documents first)
        sorted_documents = list(document_contexts.values())
        sorted_documents.sort(key=lambda x: x['length'])
        
        # Format document context with prioritized structure
        context_pieces = []
        
        # Add document titles first
        titles_section = []
        for doc in sorted_documents:
            titles_section.append(f"{doc['title']}")
        
        # Add chapters section next
        chapters_section = []
        for doc in sorted_documents:
            if doc['chapters']:
                chapters_section.append(f"--- CHAPTERS FROM {doc['title']} ---\n{doc['chapters']}")
        
        # Add headings section next
        headings_section = []
        for doc in sorted_documents:
            if doc['headings']:
                headings_section.append(f"--- HEADINGS FROM {doc['title']} ---\n{doc['headings']}")
        
        # Add main content last
        content_section = []
        for doc in sorted_documents:
            # Build full document structure
            doc_header = f"--- DOCUMENT CONTENT: {doc['title']} ---"
            
            # Highlight shorter documents (less than 1000 characters)
            if doc['length'] < 1000:
                doc_header = f"⭐⭐⭐ IMPORTANT DOCUMENT ⭐⭐⭐\n{doc_header}\n⭐⭐⭐ PLEASE READ CAREFULLY ⭐⭐⭐"
            
            content_section.append(f"{doc_header}\n{doc['content']}\n")
        
        # Combine all sections with clear section headers
        result = "### DOCUMENT TITLES ###\n" + "\n".join(titles_section) + "\n\n"
        
        if chapters_section:
            result += "### DOCUMENT CHAPTERS ###\n" + "\n\n".join(chapters_section) + "\n\n"
        
        if headings_section:
            result += "### DOCUMENT HEADINGS ###\n" + "\n\n".join(headings_section) + "\n\n"
        
        result += "### DOCUMENT CONTENT ###\n" + "\n".join(content_section)
        
        print(f"Returning {len(result)} characters of document context with prioritized structure")
        
        return result
    
    except Exception as e:
        print(f"Error extracting document context: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return f"[Error extracting document context: {str(e)}]"

def get_relevant_chunks(text: str, query: str, max_chunks: int = 5, chunk_size: int = 10000) -> List[str]:
    """
    Split text into chunks and return the most relevant ones based on the query.
    
    Args:
        text: The full text to chunk
        query: The search query
        max_chunks: Maximum number of chunks to return
        chunk_size: Size of each chunk in characters
        
    Returns:
        List of the most relevant text chunks
    """
    # Simple semantic chunking - split by paragraphs first
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Create chunks of approximately chunk_size characters
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    print(f"Split document into {len(chunks)} chunks of approximately {chunk_size} characters each")
    
    # Score chunks based on keyword matching with the query
    # This is a simple approach - in production, you'd use embeddings and vector similarity
    scored_chunks = []
    query_terms = query.lower().split()
    
    for chunk in chunks:
        score = 0
        chunk_lower = chunk.lower()
        
        # Score based on term frequency
        for term in query_terms:
            if len(term) > 2:  # Ignore very short terms
                score += chunk_lower.count(term)
        
        # Bonus for terms appearing close together
        for i in range(len(query_terms) - 1):
            if len(query_terms[i]) > 2 and len(query_terms[i+1]) > 2:
                pair = f"{query_terms[i]} {query_terms[i+1]}"
                if pair in chunk_lower:
                    score += 5  # Bonus for adjacent terms
        
        # Bonus for terms appearing in the same paragraph
        for para in chunk.split("\n\n"):
            para_lower = para.lower()
            term_count = sum(1 for term in query_terms if len(term) > 2 and term in para_lower)
            if term_count > 1:
                score += term_count * 2  # Bonus for multiple terms in same paragraph
        
        scored_chunks.append((chunk, score))
    
    # Sort by score (highest first) and take the top max_chunks
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    # Always include the first chunk (often contains important introductory information)
    if chunks and chunks[0] not in [c[0] for c in scored_chunks[:max_chunks]]:
        scored_chunks = [(chunks[0], 0)] + scored_chunks
    
    # Take top chunks plus first chunk if needed
    top_chunks = [c[0] for c in scored_chunks[:max_chunks]]
    
    print(f"Selected {len(top_chunks)} most relevant chunks based on query: '{query[:50]}...' (truncated)")
    
    # Print scores for debugging
    for i, (chunk, score) in enumerate(scored_chunks[:max_chunks]):
        print(f"Chunk {i+1} score: {score} (length: {len(chunk)} chars)")
    
    return top_chunks

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text from a PDF file with structure prioritization.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing structured text with title, headings, and content
    """
    try:
        print(f"Extracting text from PDF: {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            error_msg = f"PDF file not found: {pdf_path}"
            print(error_msg)
            return {"error": error_msg}
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        print(f"PDF file size: {file_size} bytes")
        
        if file_size == 0:
            error_msg = f"PDF file is empty: {pdf_path}"
            print(error_msg)
            return {"error": error_msg}
        
        # Check if file is a valid PDF by reading the first few bytes
        with open(pdf_path, 'rb') as f:
            header = f.read(5)
            print(f"File header: {header}")
            if header != b'%PDF-':
                error_msg = f"File is not a valid PDF (header: {header}): {pdf_path}"
                print(error_msg)
                
                # If it's an HTML file, try to extract text from it
                if header.startswith(b'<!DOC') or header.startswith(b'<html'):
                    print(f"File appears to be HTML, attempting to extract text")
                    with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as html_file:
                        html_content = html_file.read()
                        # Very basic HTML text extraction
                        text = re.sub(r'<[^>]+>', ' ', html_content)
                        text = re.sub(r'\s+', ' ', text).strip()
                        if text:
                            print(f"Extracted {len(text)} characters from HTML")
                            # Try to extract title from HTML
                            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
                            title = title_match.group(1) if title_match else os.path.basename(pdf_path)
                            
                            # Try to extract headings from HTML
                            headings = []
                            for i in range(1, 7):  # h1 through h6
                                heading_matches = re.findall(f'<h{i}[^>]*>(.*?)</h{i}>', html_content, re.IGNORECASE)
                                for match in heading_matches:
                                    headings.append(f"{'#' * i} {re.sub(r'<[^>]+>', '', match)}")
                            
                            return {
                                "title": title,
                                "headings": "\n".join(headings),
                                "content": text,
                                "total_chars": len(text)
                            }
                        else:
                            return {"error": "File appears to be HTML but no text could be extracted"}
                
                return {"error": error_msg}
        
        # Create PDF reader
        print("Creating PDF reader")
        with open(pdf_path, 'rb') as file:
            try:
                reader = PyPDF2.PdfReader(file)
                print(f"PDF reader created successfully")
                
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    print("PDF is encrypted, attempting to decrypt")
                    try:
                        reader.decrypt('')  # Try empty password
                        print("PDF decrypted successfully")
                    except Exception as e:
                        error_msg = f"Failed to decrypt PDF: {str(e)}"
                        print(error_msg)
                        return {"error": error_msg}
                
                # Get number of pages
                num_pages = len(reader.pages)
                print(f"PDF has {num_pages} pages")
                
                if num_pages == 0:
                    error_msg = "PDF has 0 pages"
                    print(error_msg)
                    return {"error": error_msg}
                
                # Extract document title from metadata if available
                title = os.path.basename(pdf_path)  # Default to filename
                try:
                    if reader.metadata and hasattr(reader.metadata, 'title') and reader.metadata.title:
                        title = reader.metadata.title
                        print(f"Extracted title from metadata: {title}")
                except:
                    print("Could not extract title from metadata")
                
                # Lists to store different components
                headings = []
                chapters = []
                content_blocks = []
                total_chars = 0
                
                # Function to identify if text looks like a heading or chapter
                def is_heading(text):
                    # Check if line is all caps, starts with Chapter, or matches common heading patterns
                    text = text.strip()
                    if not text:
                        return False
                    if text.isupper() and len(text) > 3 and len(text) < 100:
                        return True
                    if re.match(r'^(CHAPTER|Chapter|Section|SECTION|PART|Part)\s+\d+', text):
                        return True
                    if re.match(r'^\d+\.\s+[A-Z]', text) and len(text) < 100:  # Numbered sections like "1. INTRODUCTION"
                        return True
                    if re.match(r'^[IVXLCDM]+\.\s+[A-Z]', text) and len(text) < 100:  # Roman numerals
                        return True
                    return False
                
                # Extract text from each page
                for i in range(num_pages):
                    try:
                        page = reader.pages[i]
                        page_text = page.extract_text()
                        
                        if page_text:
                            # Process page text to identify structure
                            lines = page_text.split('\n')
                            page_content = []
                            
                            for line in lines:
                                line = line.strip()
                                if line:
                                    if is_heading(line):
                                        if "chapter" in line.lower() or "section" in line.lower():
                                            chapters.append(line)
                                        else:
                                            headings.append(line)
                                    else:
                                        page_content.append(line)
                            
                            # Add page content to content blocks
                            if page_content:
                                page_content_text = "\n".join(page_content)
                                content_blocks.append(page_content_text)
                                total_chars += len(page_content_text)
                            
                            print(f"Processed page {i+1}: found {len(page_content)} content lines")
                        else:
                            print(f"No text extracted from page {i+1}")
                    except Exception as e:
                        error_msg = f"Error extracting text from page {i+1}: {str(e)}"
                        print(error_msg)
                        content_blocks.append(f"[Error on page {i+1}: {error_msg}]")
                
                # Create structured result
                result = {
                    "title": title,
                    "chapters": "\n".join(chapters),
                    "headings": "\n".join(headings),
                    "content": "\n\n".join(content_blocks),
                    "total_chars": total_chars
                }
                
                print(f"Total characters extracted: {total_chars}")
                print(f"Identified {len(chapters)} chapters and {len(headings)} headings")
                
                if total_chars == 0:
                    # Try alternative extraction method
                    print("No text extracted, trying alternative extraction method")
                    try:
                        from pdfminer.high_level import extract_text as pdfminer_extract_text
                        alt_text = pdfminer_extract_text(pdf_path)
                        if alt_text:
                            print(f"Alternative extraction successful: {len(alt_text)} characters")
                            result = {
                                "title": title,
                                "chapters": "",
                                "headings": "",
                                "content": alt_text,
                                "total_chars": len(alt_text)
                            }
                            return result
                        else:
                            print("Alternative extraction also failed")
                    except Exception as e:
                        print(f"Alternative extraction error: {str(e)}")
                        # Continue with original result
                
                return result
                
            except Exception as e:
                error_msg = f"Error reading PDF: {str(e)}"
                print(error_msg)
                print(f"Traceback: {traceback.format_exc()}")
                return {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Unexpected error extracting text from PDF: {str(e)}"
        print(error_msg)
        print(f"Traceback: {traceback.format_exc()}")
        return {"error": error_msg}

def get_file_mimetype(filename: str) -> str:
    """
    Get the MIME type for a file based on its extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type is None:
        # Default to binary if type can't be determined
        return 'application/octet-stream'
    return mime_type

def get_file_type(filename: str) -> str:
    """
    Get the file type (extension) from a filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File type (e.g., PDF, DOCX, XLSX)
    """
    _, ext = os.path.splitext(filename)
    if ext:
        return ext[1:].upper()  # Remove the dot and convert to uppercase
    return "UNKNOWN"

async def list_documents(db: Session, current_user_id: int) -> List[Dict]:
    """
    List all documents for the current user.
    
    Args:
        db: Database session
        current_user_id: ID of the current user
        
    Returns:
        List of document records
    """
    print(f"[DEBUG] list_documents called for user ID: {current_user_id}")
    
    # Only return documents that belong to the current user
    documents = db.query(Document).filter(
        Document.uploaded_by == current_user_id,
        Document.is_deleted == False
    ).all()
    
    print(f"[DEBUG] Found {len(documents)} documents for user {current_user_id}")
    for doc in documents:
        print(f"[DEBUG]   Document: id={doc.id}, filename={doc.filename}, uploaded_by={doc.uploaded_by}")
    
    result = [
        {
            "id": doc.id,
            "filename": doc.filename,
            "filepath": doc.filepath,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "uploaded_at": doc.uploaded_at,
            "uploaded_by": doc.uploaded_by
        }
        for doc in documents
    ]
    
    print(f"[DEBUG] Returning {len(result)} document records")
    return result

async def get_document(doc_id: int, db: Session, current_user_id: int) -> Optional[Dict]:
    """
    Get a document by ID, ensuring it belongs to the current user.
    
    Args:
        doc_id: ID of the document to get
        db: Database session
        current_user_id: ID of the current user
        
    Returns:
        Document record or None if not found or not owned by the user
    """
    # Only return the document if it belongs to the current user
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.uploaded_by == current_user_id,
        Document.is_deleted == False
    ).first()
    
    if not doc:
        return None
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "filepath": doc.filepath,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "uploaded_at": doc.uploaded_at,
        "uploaded_by": doc.uploaded_by
    }

async def assign_default_pdf_to_user(user_id: int, db: Session) -> Optional[Dict]:
    """
    Assign the Chapter 746 Centers PDF to a new user.
    This function is called during user registration to ensure all users have access to the minimum standards.
    
    Args:
        user_id: ID of the user to assign the PDF to
        db: Database session
        
    Returns:
        Document record or None if the operation failed
    """
    try:
        # Check if the user already has the Chapter 746 Centers PDF
        existing_doc = db.query(Document).filter(
            Document.uploaded_by == user_id,
            Document.filename == "chapter-746-centers.pdf",
            Document.is_deleted == False
        ).first()
        
        if existing_doc:
            print(f"User {user_id} already has the Chapter 746 Centers PDF assigned")
            return {
                "id": existing_doc.id,
                "filename": existing_doc.filename,
                "filepath": existing_doc.filepath,
                "file_type": existing_doc.file_type,
                "file_size": existing_doc.file_size,
                "uploaded_at": existing_doc.uploaded_at,
                "uploaded_by": existing_doc.uploaded_by
            }
        
        # Ensure the PDF exists in the storage directory
        source_path = os.path.join(settings.PDF_STORAGE_PATH, "chapter-746-centers.pdf")
        if not os.path.exists(source_path):
            print(f"Error: Chapter 746 Centers PDF not found at {source_path}")
            return None
        
        # Generate a unique filename for this user's copy
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_chapter-746-centers.pdf"
        
        # Create a new document record in the database
        file_size = os.path.getsize(source_path)
        document = Document(
            filename="chapter-746-centers.pdf",
            filepath=unique_filename,
            file_type="application/pdf",
            file_size=file_size,
            uploaded_by=user_id
        )
        
        # Add the document to the database
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create a copy of the file for this user
        dest_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
        shutil.copy2(source_path, dest_path)
        
        print(f"Successfully assigned Chapter 746 Centers PDF to user {user_id}")
        
        return {
            "id": document.id,
            "filename": document.filename,
            "filepath": document.filepath,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "uploaded_at": document.uploaded_at,
            "uploaded_by": document.uploaded_by
        }
    except Exception as e:
        print(f"Error assigning Chapter 746 Centers PDF to user {user_id}: {str(e)}")
        traceback.print_exc()
        return None

def index_existing_documents():
    """
    Index all existing documents in the database for AI search.
    This function is called at startup to ensure all documents are indexed.
    """
    try:
        print("Indexing existing documents for AI search...")
        # Create a database session
        from app.database import SessionLocal
        db = SessionLocal()
        
        # Get all non-deleted documents
        documents = db.query(Document).filter(Document.is_deleted == False).all()
        print(f"Found {len(documents)} documents to index")
        
        # Process each document
        for doc in documents:
            try:
                # Check if document is already indexed
                index_path = get_document_index_path(doc.id)
                if os.path.exists(index_path):
                    print(f"Document {doc.id} ({doc.filename}) is already indexed")
                    continue
                
                # Get the full path to the document
                doc_path = doc.filepath
                if not os.path.isabs(doc_path):
                    doc_path = os.path.join(settings.PDF_STORAGE_PATH, doc_path)
                
                # Check if the file exists
                if not os.path.exists(doc_path):
                    print(f"Warning: Document {doc.id} file not found at {doc_path}")
                    
                    # Try alternative paths
                    alternative_paths = [
                        os.path.join(settings.PDF_STORAGE_PATH, os.path.basename(doc.filepath)),
                        os.path.join(settings.PDF_STORAGE_PATH, doc.filename)
                    ]
                    
                    found = False
                    for alt_path in alternative_paths:
                        if os.path.exists(alt_path):
                            doc_path = alt_path
                            found = True
                            print(f"Found document at alternative path: {alt_path}")
                            break
                    
                    if not found:
                        print(f"Document {doc.id} file not found, skipping indexing")
                        continue
                
                print(f"Indexing document: {doc.filename} (ID: {doc.id})")
                
                # Extract text from the document
                if doc.file_type.lower() == 'pdf' or doc.filename.lower().endswith('.pdf'):
                    extracted_data = extract_text_from_pdf(doc_path)
                    
                    if isinstance(extracted_data, dict) and "error" not in extracted_data:
                        # Create index for this document
                        title_text = extracted_data.get("title", doc.filename)
                        chapters_text = extracted_data.get("chapters", "")
                        headings_text = extracted_data.get("headings", "")
                        content_text = extracted_data.get("content", "")
                        
                        if len(content_text) > 1000:  # Only index documents with substantial content
                            success = create_document_index(
                                doc.id, 
                                content_text,
                                title_text,
                                chapters_text,
                                headings_text
                            )
                            
                            if success:
                                print(f"Successfully indexed document: {doc.filename} (ID: {doc.id})")
                            else:
                                print(f"Failed to index document: {doc.filename} (ID: {doc.id})")
                        else:
                            print(f"Document {doc.id} is too small to index ({len(content_text)} chars)")
                    else:
                        error = extracted_data.get("error", "Unknown error") if isinstance(extracted_data, dict) else "Unknown error"
                        print(f"Error extracting text from document {doc.id}: {error}")
                else:
                    print(f"Document {doc.id} is not a PDF, skipping indexing")
                
            except Exception as e:
                print(f"Error indexing document {doc.id}: {str(e)}")
                traceback.print_exc()
        
        print("Document indexing completed")
    except Exception as e:
        print(f"Error in index_existing_documents: {str(e)}")
        traceback.print_exc()
    finally:
        db.close() 