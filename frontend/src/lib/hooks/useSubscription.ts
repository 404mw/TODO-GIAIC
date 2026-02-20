import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import {
  SubscriptionResponseSchema,
  CancelSubscriptionResponseSchema
} from '@/lib/schemas/subscription.schema';
import { z } from 'zod';

// Get current subscription status
export function useSubscription() {
  return useQuery({
    queryKey: ['subscription'],
    queryFn: () => apiClient.get('/subscription', z.object({ data: SubscriptionResponseSchema })),
  });
}

// Upgrade subscription to Pro — calls POST /subscription/upgrade (BUG-08 fix)
export function useUpgradeSubscription() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () =>
      apiClient.post('/subscription/upgrade', {}, z.object({ data: SubscriptionResponseSchema })),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      router.push('/dashboard');
    },
  });
}

// Cancel subscription (access continues until period end)
export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiClient.post('/subscription/cancel', {}, z.object({ data: CancelSubscriptionResponseSchema })),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
    },
  });
}
