import { apiClient } from '@/lib/api/client';
import {
  UserResponseSchema,
  UserUpdateResponseSchema,
  UpdateUserRequestSchema,
  type User,
  type UpdateUserRequest,
  type UserResponse,
  type UserUpdateResponse,
} from '@/lib/schemas/user.schema';

/**
 * Users Service
 * Handles user profile operations
 * API.md: Users section
 */
export const usersService = {
  /**
   * Get authenticated user's profile information
   * API.md: GET /api/v1/users/me
   *
   * @returns User profile wrapped in DataResponse
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await usersService.getCurrentUser();
   * const user = response.data;
   * console.log(user.email, user.name, user.tier);
   * ```
   */
  async getCurrentUser(): Promise<UserResponse> {
    const response = await apiClient.get<UserResponse>(
      '/users/me',
      UserResponseSchema
    );

    return response;
  },

  /**
   * Update authenticated user's profile
   * API.md: PATCH /api/v1/users/me
   *
   * @param data - User update request (name, timezone)
   * @returns Updated user profile wrapped in DataResponse
   * @throws ApiError with code VALIDATION_ERROR if invalid data (name 1-100 chars, valid timezone)
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await usersService.updateCurrentUser({
   *   name: 'Jane Doe',
   *   timezone: 'America/Los_Angeles'
   * });
   * const updatedUser = response.data;
   * ```
   */
  async updateCurrentUser(data: UpdateUserRequest): Promise<UserUpdateResponse> {
    // Validate request schema
    UpdateUserRequestSchema.parse(data);

    const response = await apiClient.patch<UserUpdateResponse>(
      '/users/me',
      data,
      UserUpdateResponseSchema
    );

    return response;
  },
};
