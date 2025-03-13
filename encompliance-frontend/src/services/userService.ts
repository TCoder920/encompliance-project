import api, { authApi } from './api';

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
    try {
      // Use the new getUserInfo method which tries multiple approaches
      console.log('Getting current user with getUserInfo method');
      return await authApi.getUserInfo();
    } catch (error) {
      console.error('All getUserInfo attempts failed:', error);
      // If we can't get the user, clear the token and throw
      localStorage.removeItem('token');
      throw new Error('Failed to authenticate user. Please log in again.');
    }
  },
  
  async updateCurrentUser(data: UserUpdateData): Promise<UserData> {
    const response = await api.put('/users/me', data);
    return response.data;
  },
  
  // Special debug method
  async testAuth(): Promise<any> {
    try {
      const response = await api.get('/users/auth-debug');
      return response.data;
    } catch (error) {
      console.error('Auth debug error:', error);
      throw error;
    }
  }
}; 