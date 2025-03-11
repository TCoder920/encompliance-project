import api from './api';

export interface SignupData {
  email: string;
  password: string;
  full_name: string;
  operation_name: string;
  operation_type?: string;
  state?: string;
  phone_number?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async signup(data: SignupData): Promise<AuthResponse> {
    const response = await api.post('/signup', data);
    return response.data;
  },

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await api.post('/email-login', data);
    return response.data;
  },

  async refreshToken(): Promise<AuthResponse> {
    const response = await api.post('/refresh-token');
    return response.data;
  },

  setToken(token: string): void {
    localStorage.setItem('token', token);
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },

  removeToken(): void {
    localStorage.removeItem('token');
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}; 