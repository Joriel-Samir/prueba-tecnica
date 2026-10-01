import type { Activity, Associate, AuthSession, BulkUploadResult, LoginRequest, RegisterRequest, Role } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const SESSION_STORAGE_KEY = 'ihungo-session';

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly details?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export function getApiFieldErrors(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || !error.details || typeof error.details !== 'object') return {};
  const details = error.details as Record<string, unknown>;
  const source = details.details && typeof details.details === 'object'
    ? details.details as Record<string, unknown>
    : details;
  return Object.fromEntries(Object.entries(source).map(([key, value]) => [
    key,
    Array.isArray(value) ? value.join(' ') : String(value),
  ]));
}

function decodeRole(accessToken: string): Role | undefined {
  try {
    const payload = accessToken.split('.')[1];
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/'))) as { role?: Role };
    return decoded.role;
  } catch {
    return undefined;
  }
}

export function getStoredSession(): AuthSession | null {
  const rawValue = window.localStorage.getItem(SESSION_STORAGE_KEY);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as AuthSession;
  } catch {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
}

export function persistSession(session: AuthSession | null): void {
  if (!session) {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

function getErrorMessage(body: unknown, status: number): { message: string; details?: unknown } {
  if (body && typeof body === 'object' && 'error' in body) {
    const error = (body as { error?: { message?: string; details?: unknown } }).error;
    if (error?.message) {
      return { message: error.message, details: error.details };
    }
  }

  if (body && typeof body === 'object') {
    return { message: Object.values(body).flat().join(' ') || `Error de API (${status})`, details: body };
  }

  return { message: `Error de API (${status})` };
}

async function request<T>(endpoint: string, options: RequestInit = {}, retry = true): Promise<T> {
  const session = getStoredSession();
  const headers = new Headers(options.headers ?? {});

  headers.set('Content-Type', 'application/json');

  if (session?.access) {
    headers.set('Authorization', `Bearer ${session.access}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && retry && session?.refresh && !endpoint.endsWith('/token/refresh/')) {
    const refreshed = await refreshSession(session);
    if (refreshed) {
      return request<T>(endpoint, options, false);
    }
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = getErrorMessage(body, response.status);
    throw new ApiError(error.message, response.status, error.details);
  }

  return body as T;
}

async function refreshSession(session: AuthSession): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/api/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: session.refresh }),
  });

  if (!response.ok) {
    persistSession(null);
    return false;
  }

  const result = (await response.json()) as { access: string };
  persistSession({ ...session, access: result.access });
  return true;
}

function toActivity(raw: Record<string, unknown>): Activity {
  const associated = raw.asociado;
  const associatedObject = typeof associated === 'object' && associated !== null
    ? associated as Record<string, unknown>
    : undefined;

  return {
    id: String(raw.id),
    title: String(raw.tipo ?? ''),
    notes: String(raw.descripcion ?? ''),
    start: String(raw.fecha_inicio),
    end: String(raw.fecha_fin),
    assignee: associatedObject
      ? `${associatedObject.nombre ?? ''} ${associatedObject.apellidos ?? ''}`.trim() || String(associatedObject.email ?? associatedObject.id)
      : String(associated ?? ''),
    assigneeId: Number(associatedObject?.id ?? associated),
  };
}

function toAssociate(raw: Record<string, unknown>): Associate {
  return {
    id: Number(raw.id),
    identification: String(raw.identificacion ?? ''),
    name: String(raw.nombre ?? ''),
    lastName: String(raw.apellidos ?? ''),
    email: String(raw.email ?? ''),
    city: String(raw.ciudad ?? ''),
  };
}

function toApiActivity(payload: Partial<Activity>, requireAssignee = false): Record<string, unknown> {
  if (requireAssignee && !payload.assigneeId && payload.assigneeId !== 0) {
    throw new ApiError('Selecciona un asociado para la actividad.', 400);
  }

  return {
    ...(payload.title !== undefined ? { tipo: payload.title } : {}),
    ...(payload.notes !== undefined ? { descripcion: payload.notes } : {}),
    ...(payload.start !== undefined ? { fecha_inicio: payload.start } : {}),
    ...(payload.end !== undefined ? { fecha_fin: payload.end } : {}),
    ...(payload.assigneeId !== undefined ? { asociado: payload.assigneeId } : {}),
  };
}

export const api = {
  login: async (payload: LoginRequest): Promise<AuthSession> => {
    const result = await request<{ access: string; refresh: string; role?: Role }>('/api/auth/token/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    return {
      access: result.access,
      refresh: result.refresh,
      user: { id: payload.email, name: payload.email.split('@')[0], email: payload.email, role: result.role ?? decodeRole(result.access) ?? 'associate' },
    };
  },
  register: async (payload: RegisterRequest): Promise<{ message: string }> => {
    await request('/api/registro/', {
      method: 'POST',
      body: JSON.stringify({ nombre: payload.name, email: payload.email, password: payload.password }),
    });
    return { message: 'Solicitud enviada. Tu cuenta está pendiente de aprobación.' };
  },
  getActivities: async (desde?: string, hasta?: string): Promise<Activity[]> => {
    const params = new URLSearchParams();
    if (desde) params.set('desde', desde);
    if (hasta) params.set('hasta', hasta);
    const query = params.toString();
    const response = await request<unknown>(`/api/actividades/${query ? `?${query}` : ''}`);
    const activities = Array.isArray(response)
      ? response
      : ((response as { results?: unknown[] }).results ?? []);
    return activities.map((activity) => toActivity(activity as Record<string, unknown>));
  },
  getAssociates: async (): Promise<Associate[]> => {
    const response = await request<unknown>('/api/asociados/');
    const associates = Array.isArray(response)
      ? response
      : ((response as { results?: unknown[] }).results ?? []);
    return associates.map((associate) => toAssociate(associate as Record<string, unknown>));
  },
  uploadBulk: async (file: File, endpoint: string): Promise<BulkUploadResult> => {
    const session = getStoredSession();
    const formData = new FormData();
    formData.append('file', file);
    const headers = new Headers();
    if (session?.access) headers.set('Authorization', `Bearer ${session.access}`);
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      const error = getErrorMessage(body, response.status);
      throw new ApiError(error.message, response.status, error.details);
    }
    return body as BulkUploadResult;
  },
  uploadAssociates: async (file: File): Promise<BulkUploadResult> => api.uploadBulk(file, '/api/carga-masiva/asociados/'),
  uploadActivities: async (file: File): Promise<BulkUploadResult> => api.uploadBulk(file, '/api/cargamasiva/actividades/'),
  createActivity: async (payload: Partial<Activity>): Promise<Activity> => {
    const created = await request<Record<string, unknown>>('/api/actividades/', {
      method: 'POST',
      body: JSON.stringify(toApiActivity(payload, true)),
    });
    return toActivity(created);
  },
  updateActivity: async (id: string, payload: Partial<Activity>): Promise<Activity> => {
    const updated = await request<Record<string, unknown>>(`/api/actividades/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(toApiActivity(payload)),
    });
    return toActivity(updated);
  },
  deleteActivity: async (id: string): Promise<void> => {
    await request<void>(`/api/actividades/${id}/`, { method: 'DELETE' });
  },
};
