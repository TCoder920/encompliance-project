import api from './api';

export interface PDF {
  id: number;
  filename: string;
  filepath: string;
  uploaded_at: string;
  uploaded_by: number;
  is_deleted: boolean;
  deleted_at: string | null;
  deleted_by: number | null;
}

export interface PDFListResponse {
  pdfs: PDF[];
}

class PDFService {
  async uploadPDF(file: File): Promise<PDF> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/pdfs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async listPDFs(): Promise<PDF[]> {
    const response = await api.get<PDFListResponse>('/pdfs/list');
    return response.data.pdfs;
  }

  async downloadPDF(pdfId: number): Promise<string> {
    const response = await api.get<PDF>(`/pdfs/download/${pdfId}`);
    return response.data.filepath;
  }

  async deletePDF(pdfId: number): Promise<PDF> {
    const response = await api.delete<PDF>(`/pdfs/delete/${pdfId}`);
    return response.data;
  }
}

export default new PDFService(); 