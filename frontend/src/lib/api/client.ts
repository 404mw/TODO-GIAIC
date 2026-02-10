import { z } from 'zod';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

function generateIdempotencyKey(): string {
  // Generate UUID v4 for idempotency key (FR-059)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older browsers
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

async function handleResponse<T>(
  response: Response,
  schema?: z.ZodType<T>
): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    // Handle both error formats: {"error": {...}} and {"code": ..., "message": ...}
    const errorMessage = errorData.message || errorData.error?.message || 'Request failed';
    const errorCode = errorData.code || errorData.error?.code || 'UNKNOWN_ERROR';
    throw new ApiError(response.status, errorCode, errorMessage, errorData);
  }

  const data = await response.json();

  // Handle multiple backend response formats:
  // - DataResponse[T]: {"data": ...}
  // - PaginatedResponse[T]: {"data": [...], "pagination": {...}}
  // - TaskCompletionResponse: {"task": {...}}
  // - Direct object: {...}
  let payload = data;

  if (data.data !== undefined) {
    // If pagination exists, keep full structure for pagination metadata
    if (data.pagination !== undefined) {
      payload = data; // Keep {data: [...], pagination: {...}}
    } else {
      payload = data.data; // Extract just the data
    }
  } else if (data.task !== undefined) {
    payload = data; // Keep {task: {...}} structure
  }
  // Otherwise return as-is (direct object response)

  return schema ? schema.parse(payload) : payload;
}

export const apiClient = {
  async get<T>(endpoint: string, schema?: z.ZodType<T>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(getAuthToken() && { Authorization: `Bearer ${getAuthToken()}` }),
      },
    });
    return handleResponse(response, schema);
  },

  async post<T>(endpoint: string, body: unknown, schema?: z.ZodType<T>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': generateIdempotencyKey(),
        ...(getAuthToken() && { Authorization: `Bearer ${getAuthToken()}` }),
      },
      body: JSON.stringify(body),
    });
    return handleResponse(response, schema);
  },

  async put<T>(endpoint: string, body: unknown, schema?: z.ZodType<T>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(getAuthToken() && { Authorization: `Bearer ${getAuthToken()}` }),
      },
      body: JSON.stringify(body),
    });
    return handleResponse(response, schema);
  },

  async patch<T>(endpoint: string, body: unknown, schema?: z.ZodType<T>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': generateIdempotencyKey(),
        ...(getAuthToken() && { Authorization: `Bearer ${getAuthToken()}` }),
      },
      body: JSON.stringify(body),
    });
    return handleResponse(response, schema);
  },

  async delete<T>(endpoint: string, schema?: z.ZodType<T>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(getAuthToken() && { Authorization: `Bearer ${getAuthToken()}` }),
      },
    });
    return handleResponse(response, schema);
  },
};
