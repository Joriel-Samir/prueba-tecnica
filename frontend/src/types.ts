export type Role = 'admin' | 'associate';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
}

export interface Associate {
  id: number;
  identification?: string;
  name: string;
  lastName?: string;
  email: string;
  city?: string;
}

export interface AuthSession {
  access: string;
  refresh: string;
  user: User;
}

export interface Activity {
  id: string;
  title: string;
  notes?: string;
  start: string;
  end: string;
  assignee: string;
  assigneeId?: number;
  role?: Role;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface BulkUploadResult {
  total: number;
  created: number;
  errors: Array<{ row?: number; error?: string; details?: unknown }>;
}
