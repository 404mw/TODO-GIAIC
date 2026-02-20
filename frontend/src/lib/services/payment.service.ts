/**
 * Payment Service
 *
 * Handles payment operations for subscriptions and credit purchases
 * Integrates with Checkout.com via backend API
 */

import { apiClient } from '@/lib/api/client'
import { z } from 'zod'
import { SubscriptionResponseSchema } from '@/lib/schemas/subscription.schema'

/**
 * Payment types
 */
export type PaymentType = 'subscription' | 'credit_purchase'

/**
 * Create payment session request
 */
export interface CreatePaymentSessionRequest {
  type: PaymentType
  amount?: number // For credit purchases
  metadata?: Record<string, any>
}

/**
 * Payment session response
 */
export interface PaymentSession {
  session_id: string
  checkout_url: string
}

/**
 * Payment Service
 * Wrapper for payment-related API calls
 */
export const paymentService = {
  /**
   * Upgrade to Pro subscription — calls POST /subscription/upgrade
   */
  async upgradeSubscription(): Promise<void> {
    await apiClient.post(
      '/subscription/upgrade',
      {},
      z.object({ data: SubscriptionResponseSchema })
    )
  },

  /**
   * Handle payment success callback
   * Called when user returns from Checkout.com after successful payment
   *
   * @param sessionId - Checkout session ID from URL params
   */
  async handlePaymentSuccess(sessionId: string): Promise<{ success: boolean }> {
    // Backend webhook handles the actual subscription activation
    // This is just for client-side confirmation
    return { success: true }
  },

  /**
   * Handle payment cancellation
   * Called when user cancels payment on Checkout.com
   */
  handlePaymentCancel(): void {
    // No backend call needed, user just returned without completing payment
    console.log('Payment cancelled by user')
  },

  /**
   * Get payment status
   * Checks if a payment session was completed
   *
   * @param sessionId - Checkout session ID
   */
  async getPaymentStatus(sessionId: string): Promise<{ status: string }> {
    // In a full implementation, this would check the payment status
    // For now, we rely on the subscription status endpoint
    return { status: 'unknown' }
  },
}

/**
 * Redirect to checkout
 * Helper function to redirect user to Checkout.com payment page
 *
 * @param checkoutUrl - URL from payment session
 */
export function redirectToCheckout(checkoutUrl: string): void {
  if (typeof window !== 'undefined') {
    window.location.href = checkoutUrl
  }
}

/**
 * Get return URLs for payment flow
 * Constructs success/cancel URLs for payment callbacks
 */
export function getPaymentReturnUrls() {
  if (typeof window === 'undefined') {
    return {
      successUrl: '/dashboard/subscription/success',
      cancelUrl: '/dashboard/credits',
    }
  }

  const baseUrl = window.location.origin

  return {
    successUrl: `${baseUrl}/dashboard/subscription/success`,
    cancelUrl: `${baseUrl}/dashboard/credits`,
  }
}
