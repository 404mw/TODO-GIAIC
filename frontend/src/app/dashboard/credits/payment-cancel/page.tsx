'use client'

import Link from 'next/link'
import { XCircle, ArrowLeft, HelpCircle } from 'lucide-react'

/**
 * Payment Cancel Page
 *
 * Displayed when user cancels payment on Checkout.com
 * Provides options to retry or get help
 */
export default function PaymentCancelPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-6">
      <div className="mx-auto max-w-2xl w-full">
        {/* Cancel Card */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 md:p-12 text-center border border-gray-200 dark:border-gray-800">
          {/* Cancel Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 bg-orange-100 dark:bg-orange-900/30 rounded-full mb-6">
            <XCircle className="h-12 w-12 text-orange-600 dark:text-orange-400" />
          </div>

          {/* Cancel Message */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Payment Cancelled
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
            Your payment was not completed. No charges were made to your account.
          </p>

          {/* Reassurance */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 mb-8 border border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-3 text-left">
              <HelpCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                  Why was my payment cancelled?
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Payments can be cancelled if you closed the payment window, encountered a technical issue,
                  or decided not to complete the purchase. This is completely normal and you can try again anytime.
                </p>
              </div>
            </div>
          </div>

          {/* What to do next */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 mb-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              What would you like to do?
            </h2>
            <ul className="text-left space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Try purchasing credits again with a different payment method</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Contact our support team if you experienced a technical issue</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Continue using your current credits and return later</span>
              </li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard/credits"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-purple-600 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-700 transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Try Again
            </Link>
            <Link
              href="/contact"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-3 text-sm font-semibold text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Contact Support
            </Link>
          </div>

          {/* Back to Dashboard */}
          <div className="mt-8">
            <Link
              href="/dashboard"
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
