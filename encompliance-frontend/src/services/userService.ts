import api from './api';

export interface UserData {
  id: number;
  email: string;
  full_name: string;
  operation_name: string;
  operation_type?: string;
  state?: string;
  phone_number?: string;
  subscription_status: string;
  subscription_end_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserUpdateData {
  email?: string;
  full_name?: string;
  operation_name?: string;
  operation_type?: string;
  state?: string;
  phone_number?: string;
  password?: string;
}

export const userService = {
  async getCurrentUser(): Promise<UserData> {
    const response = await api.get('/users/me');
    return response.data;
  },
  
  async updateCurrentUser(data: UserUpdateData): Promise<UserData> {
    const response = await api.put('/users/me', data);
    return response.data;
  }
}; 