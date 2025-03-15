import documentService, { Document } from './documentService';

// Alias Document as PDF for backward compatibility
export type PDF = Document;

export interface PDFListResponse {
  pdfs: PDF[];
}

class PDFService {
  async uploadPDF(file: File): Promise<PDF> {
    try {
      console.log('PDFService: Uploading file via documentService:', file.name);
      const result = await documentService.uploadDocument(file);
      console.log('PDFService: Upload successful, document ID:', result.id);
      return result;
    } catch (err) {
      console.error('PDFService: Error uploading file:', err);
      throw err;
    }
  }

  async listPDFs(): Promise<PDF[]> {
    try {
      console.log('PDFService: Listing PDFs via documentService');
      const documents = await documentService.listDocuments();
      console.log(`PDFService: Found ${documents.length} documents`);
      return documents;
    } catch (err) {
      console.error('PDFService: Error listing PDFs:', err);
      return [];
    }
  }

  async downloadPDF(pdfId: number): Promise<string> {
    try {
      console.log(`PDFService: Downloading PDF ${pdfId} via documentService`);
      return await documentService.downloadDocument(pdfId.toString());
    } catch (err) {
      console.error(`PDFService: Error downloading PDF ${pdfId}:`, err);
      throw err;
    }
  }

  async deletePDF(pdfId: number): Promise<PDF> {
    try {
      console.log(`PDFService: Deleting PDF ${pdfId} via documentService`);
      return await documentService.deleteDocument(pdfId);
    } catch (err) {
      console.error(`PDFService: Error deleting PDF ${pdfId}:`, err);
      throw err;
    }
  }
}

export default new PDFService(); 