import api from './api';
import docLogger from '../utils/documentLogger';

// In Vite, environment variables are accessed via import.meta.env
// See: https://vitejs.dev/guide/env-and-mode.html
const backendUrl = (import.meta.env.VITE_BACKEND_URL as string) || 'http://localhost:8000';

export interface Document {
  id: number;
  filename: string;
  filepath: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  uploaded_by: number;
  is_deleted: boolean;
  deleted_at: string | null;
  deleted_by: number | null;
}

export interface DocumentListResponse {
  documents: Document[];
}

class DocumentService {
  async uploadDocument(file: File): Promise<Document> {
    const operation = docLogger.start('uploadDocument', { fileName: file.name, fileSize: file.size });
    try {
      docLogger.log(`Uploading document: ${file.name} (${file.size} bytes)`);
      const formData = new FormData();
      formData.append('file', file);

      console.log(`[DEBUG] Starting document upload request for ${file.name}`);
      
      const response = await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log(`[DEBUG] Document upload response:`, response);
      if (!response.data) {
        console.error('[DEBUG] Document upload response missing data');
      } else if (!response.data.id) {
        console.error('[DEBUG] Document upload response missing ID', response.data);
      } else {
        console.log(`[DEBUG] Document uploaded successfully with ID: ${response.data.id}`);
      }

      docLogger.success('Document upload successful', { 
        documentId: response.data.id, 
        filename: response.data.filename 
      });
      return response.data;
    } catch (err) {
      console.error('[DEBUG] Document upload error:', err);
      docLogger.error('Error uploading document', err);
      throw err; // Rethrow to allow components to handle the error
    } finally {
      if (operation) {
        docLogger.end(operation);
      }
    }
  }

  async listDocuments(): Promise<Document[]> {
    const operation = docLogger.start('listDocuments');
    try {
      docLogger.log('Fetching documents from API...');
      let attempts = 0;
      const maxAttempts = 2;
      
      console.log(`[DEBUG] Starting document list request`);
      
      while (attempts < maxAttempts) {
        try {
          attempts++;
          docLogger.log(`Attempt ${attempts}/${maxAttempts} to fetch documents`);
          const response = await api.get<DocumentListResponse>('/documents/list');
          console.log(`[DEBUG] Document list response:`, response);
          
          docLogger.log(`Documents API response (attempt ${attempts}):`, response.data);
          
          if (response.data && Array.isArray(response.data.documents)) {
            console.log(`[DEBUG] Found ${response.data.documents.length} documents:`, response.data.documents);
            docLogger.success(`Found ${response.data.documents.length} documents`);
            
            // Log each document for debugging
            response.data.documents.forEach((doc, index) => {
              docLogger.log(`Document ${index + 1}:`, {
                id: doc.id,
                filename: doc.filename,
                uploaded_at: doc.uploaded_at,
                file_type: doc.file_type,
                filepath: doc.filepath
              });
            });
            
            // Cache documents locally (could use localStorage or state management)
            window.localStorage.setItem('cachedDocuments', JSON.stringify(response.data.documents));
            
            return response.data.documents;
          } else {
            console.error(`[DEBUG] Unexpected document list response format:`, response.data);
            docLogger.warn('Unexpected response format:', response.data);
            if (attempts < maxAttempts) {
              docLogger.log(`Retrying document list (attempt ${attempts + 1}/${maxAttempts})...`);
              await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retry
            }
          }
        } catch (error) {
          console.error(`[DEBUG] Error in document list attempt ${attempts}:`, error);
          docLogger.error(`Error in attempt ${attempts}:`, error);
          if (attempts < maxAttempts) {
            docLogger.log(`Retrying after error (attempt ${attempts + 1}/${maxAttempts})...`);
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retry
          } else {
            throw error; // Rethrow on last attempt
          }
        }
      }
      
      docLogger.error('Failed to fetch documents after all attempts');
      
      // Try to return cached documents if any
      const cachedDocuments = window.localStorage.getItem('cachedDocuments');
      if (cachedDocuments) {
        const parsed = JSON.parse(cachedDocuments);
        console.log(`[DEBUG] Returning ${parsed.length} cached documents as fallback`);
        docLogger.warn('Returning cached documents as fallback', { count: parsed.length });
        return parsed;
      }
      
      console.log(`[DEBUG] No documents found - returning empty array`);
      return []; // Return empty array after all attempts fail
    } catch (err) {
      console.error('[DEBUG] Error fetching documents:', err);
      docLogger.error('Error fetching documents:', err);
      return []; // Return empty array on error
    } finally {
      if (operation) {
        docLogger.end(operation);
      }
    }
  }

  async downloadDocument(documentId: string): Promise<string> {
    const response = await api.get<Document>(`/documents/download/${documentId}`);
    return response.data.filepath;
  }

  async deleteDocument(documentId: number): Promise<Document> {
    const response = await api.delete<Document>(`/documents/delete/${documentId}`);
    return response.data;
  }

  // Utility function to get the authenticated URL for a document
  getAuthenticatedDocumentUrl(documentId: string): string {
    const token = localStorage.getItem('token');
    return `${backendUrl}/document/${documentId}?token=${token}`;
  }

  // Utility function to get the authenticated URL for the Minimum Standards PDF
  getAuthenticatedMinimumStandardsUrl(): string {
    return "https://www.hhs.texas.gov/sites/default/files/documents/doing-business-with-hhs/provider-portal/protective-services/ccl/min-standards/chapter-746-centers.pdf";
  }

  // Utility function to get the embeddable URL for a document (for iframe embedding)
  getEmbeddableDocumentUrl(documentId: string): string {
    const token = localStorage.getItem('token');
    console.log(`Generating embeddable URL for document ${documentId}`);
    // Point directly to the correct endpoint for viewing documents
    return `${backendUrl}/api/v1/view/${documentId}?token=${token}`;
  }

  // Utility function to get the embeddable URL for the Minimum Standards PDF
  getEmbeddableMinimumStandardsUrl(): string {
    return "https://www.hhs.texas.gov/sites/default/files/documents/doing-business-with-hhs/provider-portal/protective-services/ccl/min-standards/chapter-746-centers.pdf";
  }

  // Open document in a new tab
  openDocumentInNewTab(documentId: string): void {
    const token = localStorage.getItem('token');
    // Use the correct API endpoint for viewing documents
    const url = `${backendUrl}/api/v1/view/${documentId}?token=${token}`;
    console.log(`Opening document in new tab: ${url}`);
    window.open(url, '_blank');
  }

  // Open Minimum Standards PDF in a new tab
  openMinimumStandardsInNewTab(): void {
    const url = this.getEmbeddableMinimumStandardsUrl();
    console.log(`Opening minimum standards in new tab: ${url}`);
    window.open(url, '_blank');
  }

  /**
   * Forcefully refresh the document list cache
   * This can be called when we need to ensure we have the latest documents
   */
  async refreshDocumentCache(): Promise<Document[]> {
    const operation = docLogger.start('refreshDocumentCache');
    docLogger.log('Forcing document cache refresh');
    
    try {
      // First clear any existing cache
      localStorage.removeItem('cachedDocuments');
      docLogger.log('Document cache cleared');
      
      // Make a direct API call to ensure we get fresh data
      const response = await api.get<DocumentListResponse>('/documents/list');
      
      console.log(`[DEBUG] Direct API call for document refresh:`, response);
      
      if (response.data && Array.isArray(response.data.documents)) {
        const documents = response.data.documents;
        // Store in localStorage for backup
        localStorage.setItem('cachedDocuments', JSON.stringify(documents));
        
        // Log success with document details
        console.log(`[DEBUG] Document cache refresh successful, found ${documents.length} documents:`);
        documents.forEach((doc, i) => {
          console.log(`[DEBUG] Document ${i+1}: ID=${doc.id}, Name=${doc.filename}`);
        });
        
        docLogger.success('Document cache refreshed successfully', { count: documents.length });
        return documents;
      } else {
        // If response format is unexpected, log error and return empty array
        console.error(`[DEBUG] Unexpected response format in refreshDocumentCache:`, response.data);
        docLogger.error('Unexpected response format during cache refresh', null, { response: response.data });
        return [];
      }
    } catch (err) {
      console.error('[DEBUG] Failed to refresh document cache:', err);
      docLogger.error('Failed to refresh document cache', err);
      
      return [];
    } finally {
      if (operation) {
        docLogger.end(operation);
      }
    }
  }
}

export default new DocumentService(); 