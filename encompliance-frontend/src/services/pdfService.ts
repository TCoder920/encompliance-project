import api from './api';

export interface PDFData {
  id: number;
  title: string;
  description?: string;
  filename: string;
  file_size: number;
  file_type: string;
  category?: string;
  is_public: boolean;
  is_processed: boolean;
  created_at: string;
  updated_at: string;
}

export interface UploadResponse {
  id: number;
  title: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_success: boolean;
  message: string;
}

export const pdfService = {
  async uploadPDF(file: File, title: string, description?: string, category?: string, isPublic: boolean = false): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (description) formData.append('description', description);
    if (category) formData.append('category', category);
    formData.append('is_public', String(isPublic));
    
    const response = await api.post('/pdfs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
  
  async getUserPDFs(category?: string): Promise<PDFData[]> {
    const params = category ? { category } : {};
    const response = await api.get('/pdfs', { params });
    return response.data;
  },
  
  async getPublicPDFs(category?: string): Promise<PDFData[]> {
    const params = category ? { category } : {};
    const response = await api.get('/pdfs/public', { params });
    return response.data;
  },
  
  async getPDF(id: number): Promise<PDFData> {
    const response = await api.get(`/pdfs/${id}`);
    return response.data;
  },
  
  getDownloadURL(id: number): string {
    return `${api.defaults.baseURL}/pdfs/${id}/download`;
  },
  
  async updatePDF(id: number, data: Partial<PDFData>): Promise<PDFData> {
    const response = await api.put(`/pdfs/${id}`, data);
    return response.data;
  },
  
  async deletePDF(id: number): Promise<{ success: boolean; message: string }> {
    const response = await api.delete(`/pdfs/${id}`);
    return response.data;
  }
}; 