import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { AICreditLedgerSchema } from '@/lib/schemas/credit.schema';
import { z } from 'zod';

const CreditBalanceResponseSchema = z.object({
  data: z.object({
    daily_free: z.number(),
    subscription: z.number(),
    purchased: z.number(),
    total: z.number(),
  }),
});

const CreditHistoryResponseSchema = z.object({
  data: z.array(AICreditLedgerSchema),
});

const PurchaseCreditsResponseSchema = z.object({
  success: z.boolean(),
  credits_purchased: z.number(),
  new_balance: z.number(),
});

// Get current credit balance
export function useCreditBalance() {
  return useQuery({
    queryKey: ['credits', 'balance'],
    queryFn: () => apiClient.get('/credits/balance', CreditBalanceResponseSchema),
    staleTime: 1000 * 60 * 2, // 2 minutes - balance updates occasionally
  });
}

// Get credit transaction history
export function useCreditHistory(limit = 50) {
  return useQuery({
    queryKey: ['credits', 'history', { limit }],
    queryFn: () => apiClient.get(`/credits/history?limit=${limit}`, CreditHistoryResponseSchema),
  });
}

// Purchase additional AI credits (Pro tier only, max 500/month)
export function usePurchaseCredits() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (amount: number) =>
      apiClient.post(
        '/subscription/purchase-credits',
        { amount },
        z.object({ data: PurchaseCreditsResponseSchema })
      ),
    onSuccess: () => {
      // Invalidate both balance and history
      queryClient.invalidateQueries({ queryKey: ['credits'] });
    },
  });
}
