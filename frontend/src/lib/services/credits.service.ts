import { apiClient } from '@/lib/api/client';
import {
  CreditBalanceResponseSchema,
  CreditHistoryResponseSchema,
  type CreditBalanceResponse,
  type CreditHistoryResponse,
} from '@/lib/schemas/credit.schema';

/**
 * Credits Service
 * Handles credit balance and transaction history operations
 * API.md: Credits section
 */
export const creditsService = {
  /**
   * Get detailed credit balance breakdown
   * API.md: GET /api/v1/credits/balance
   *
   * @returns Credit balance with daily, subscription, purchased, kickstart, and total amounts
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await creditsService.getBalance();
   * const { daily, subscription, purchased, kickstart, total } = response.data;
   * console.log(`Total credits: ${total}`);
   * console.log(`Daily: ${daily}, Subscription: ${subscription}, Purchased: ${purchased}`);
   * ```
   *
   * @note Credit types:
   * - Daily: Free daily credits (expire at UTC midnight)
   * - Subscription: Pro tier monthly credits (carry over up to 50)
   * - Purchased: One-time purchased credits (never expire)
   * - Kickstart: New user bonus credits (one-time)
   */
  async getBalance(): Promise<CreditBalanceResponse> {
    const response = await apiClient.get<CreditBalanceResponse>(
      '/credits/balance',
      CreditBalanceResponseSchema
    );

    return response;
  },

  /**
   * Get paginated credit transaction history
   * API.md: GET /api/v1/credits/history
   *
   * @param offset - Pagination offset (default: 0)
   * @param limit - Items per page (max 100, default: 50)
   * @returns Paginated list of credit transactions
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code VALIDATION_ERROR if invalid pagination parameters
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await creditsService.getHistory(0, 50);
   * const transactions = response.data;
   * const { offset, limit, total } = response.pagination;
   *
   * transactions.forEach(tx => {
   *   const sign = tx.type === 'grant' ? '+' : '-';
   *   console.log(`${tx.created_at}: ${sign}${tx.amount} credits - ${tx.description}`);
   *   console.log(`  Category: ${tx.category}, Balance after: ${tx.balance_after}`);
   * });
   * ```
   *
   * @note Transaction types:
   * - grant: Credits added to account
   * - deduct: Credits consumed
   *
   * @note Categories: daily, subscription, purchase, ai, kickstart
   */
  async getHistory(offset: number = 0, limit: number = 50): Promise<CreditHistoryResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('offset', String(offset));
    queryParams.append('limit', String(limit));

    const endpoint = `/credits/history?${queryParams.toString()}`;
    const response = await apiClient.get<CreditHistoryResponse>(
      endpoint,
      CreditHistoryResponseSchema
    );

    return response;
  },
};
