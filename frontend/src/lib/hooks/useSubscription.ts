import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import {
  SubscriptionResponseSchema,
  CheckoutSessionResponseSchema,
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

// Create Checkout.com session and redirect to hosted payment page
export function useCreateCheckoutSession() {
  return useMutation({
    mutationFn: () =>
      apiClient.post('/subscription/checkout', {}, z.object({ data: CheckoutSessionResponseSchema })),
    onSuccess: (response) => {
      // Redirect to Checkout.com hosted payment page
      const checkoutUrl = response.data.checkout_url;
      if (typeof window !== 'undefined' && checkoutUrl) {
        window.location.href = checkoutUrl;
      }
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
