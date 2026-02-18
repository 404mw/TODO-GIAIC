'use client'

import { useState } from 'react'
import { useCreditBalance, useCreditHistory, usePurchaseCredits } from '@/lib/hooks/useCredits'
import { Zap, TrendingUp, Gift, CreditCard, Calendar, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

/**
 * Credits Page
 *
 * Displays user's credit balance, transaction history, and purchase options.
 * Implements Phase 3.3 of frontend updates.
 */
export default function CreditsPage() {
  const [selectedPackage, setSelectedPackage] = useState<number | null>(null)

  const { data: balanceData, isLoading: balanceLoading, error: balanceError } = useCreditBalance()
  const { data: historyData, isLoading: historyLoading } = useCreditHistory(50)
  const purchaseCredits = usePurchaseCredits()

  const balance = balanceData?.data
  const transactions = historyData?.data || []

  // Credit packages (prices in cents for backend)
  const creditPackages = [
    { credits: 10, price: 100, label: 'Starter', popular: false },
    { credits: 50, price: 400, label: 'Pro', popular: true, discount: 20 },
    { credits: 100, price: 700, label: 'Power', popular: false, discount: 30 },
  ]

  const handlePurchase = async (packageIndex: number) => {
    const pkg = creditPackages[packageIndex]

    // Confirm purchase
    const confirmed = window.confirm(
      `Purchase ${pkg.credits} credits for $${(pkg.price / 100).toFixed(2)}?`
    )

    if (!confirmed) return

    try {
      setSelectedPackage(packageIndex)
      const result = await purchaseCredits.mutateAsync(pkg.credits)

      // Show success message
      alert(`Success! Purchased ${pkg.credits} credits. New balance: ${result.data.new_balance}`)
    } catch (error) {
      console.error('Purchase failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to purchase credits'
      alert(`Error: ${errorMessage}. Please try again or contact support.`)
    } finally {
      setSelectedPackage(null)
    }
  }

  const getCreditTypeIcon = (type: string) => {
    switch (type) {
      case 'daily':
        return <Calendar className="h-4 w-4 text-blue-500" />
      case 'subscription':
        return <TrendingUp className="h-4 w-4 text-purple-500" />
      case 'purchased':
        return <CreditCard className="h-4 w-4 text-green-500" />
      case 'kickstart':
        return <Gift className="h-4 w-4 text-yellow-500" />
      default:
        return <Zap className="h-4 w-4 text-gray-500" />
    }
  }

  const formatAmount = (amount: number) => {
    const isPositive = amount > 0
    return (
      <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
        {isPositive ? '+' : ''}{amount}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-6">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Credits</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage your AI credits for generating subtasks and more
            </p>
          </div>
        </div>

        {/* Balance Overview */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {balanceLoading ? (
            <>
              {[...Array(4)].map((_, i) => (
                <div key={i} className="animate-pulse rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm">
                  <div className="h-4 w-20 bg-gray-200 dark:bg-gray-800 rounded" />
                  <div className="mt-4 h-8 w-24 bg-gray-200 dark:bg-gray-800 rounded" />
                </div>
              ))}
            </>
          ) : balanceError ? (
            <div className="col-span-4 rounded-lg bg-red-50 dark:bg-red-900/20 p-6 text-center">
              <p className="text-red-600 dark:text-red-400">Failed to load balance</p>
            </div>
          ) : (
            <>
              {/* Total Credits */}
              <div className="rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 p-6 text-white shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium opacity-90">Total Credits</span>
                  <Zap className="h-5 w-5 opacity-80" />
                </div>
                <div className="mt-4 text-4xl font-bold">{balance?.total || 0}</div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/20">
                  <div
                    className="h-full bg-white transition-all duration-300"
                    style={{ width: `${Math.min((balance?.total || 0) / 100 * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Daily Free Credits */}
              <div className="rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Daily Free</span>
                  <Calendar className="h-5 w-5 text-blue-500" />
                </div>
                <div className="mt-4 text-3xl font-bold text-gray-900 dark:text-white">
                  {balance?.daily || 0}
                </div>
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">Resets daily</p>
              </div>

              {/* Subscription Credits */}
              <div className="rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Subscription</span>
                  <TrendingUp className="h-5 w-5 text-purple-500" />
                </div>
                <div className="mt-4 text-3xl font-bold text-gray-900 dark:text-white">
                  {balance?.subscription || 0}
                </div>
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">Monthly quota</p>
              </div>

              {/* Purchased Credits */}
              <div className="rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Purchased</span>
                  <CreditCard className="h-5 w-5 text-green-500" />
                </div>
                <div className="mt-4 text-3xl font-bold text-gray-900 dark:text-white">
                  {balance?.purchased || 0}
                </div>
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">Never expires</p>
              </div>
            </>
          )}
        </div>

        {/* Purchase Credits Section */}
        <div className="rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Purchase Additional Credits
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {creditPackages.map((pkg, index) => (
              <div
                key={index}
                className={`relative rounded-lg border-2 p-6 transition-all hover:shadow-md ${
                  pkg.popular
                    ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/10'
                    : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900'
                }`}
              >
                {pkg.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-purple-500 px-3 py-1 text-xs font-semibold text-white">
                    Most Popular
                  </div>
                )}
                <div className="text-center">
                  <div className="inline-flex items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/30 p-3">
                    <Zap className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
                    {pkg.label}
                  </h3>
                  <div className="mt-2">
                    <span className="text-4xl font-bold text-gray-900 dark:text-white">
                      {pkg.credits}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">credits</span>
                  </div>
                  <div className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
                    ${(pkg.price / 100).toFixed(2)}
                  </div>
                  {pkg.discount && (
                    <div className="mt-1 text-xs text-green-600 dark:text-green-400 font-medium">
                      Save {pkg.discount}%
                    </div>
                  )}
                  <button
                    onClick={() => handlePurchase(index)}
                    disabled={selectedPackage === index || purchaseCredits.isPending}
                    className={`mt-6 w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors ${
                      pkg.popular
                        ? 'bg-purple-600 text-white hover:bg-purple-700 disabled:bg-purple-400'
                        : 'bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100 disabled:bg-gray-400 dark:disabled:bg-gray-600'
                    }`}
                  >
                    {selectedPackage === index ? 'Processing...' : 'Buy Now'}
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-lg bg-blue-50 dark:bg-blue-900/10 p-4 border border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-3">
              <Gift className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  Pro members get 100 credits monthly
                </p>
                <p className="mt-1 text-xs text-blue-700 dark:text-blue-300">
                  Upgrade to Pro for unlimited tasks, analytics, and more. Credits never expire.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Transaction History */}
        <div className="rounded-lg bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Transaction History
          </h2>
          {historyLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700" />
                    <div className="space-y-2">
                      <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
                      <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
                    </div>
                  </div>
                  <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
                </div>
              ))}
            </div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 p-4 mb-4">
                <Zap className="h-8 w-8 text-gray-400" />
              </div>
              <p className="text-gray-600 dark:text-gray-400">No transactions yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                Your credit usage history will appear here
              </p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {transactions.map((transaction) => {
                const isCredit = transaction.amount > 0
                return (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`flex items-center justify-center h-10 w-10 rounded-full ${
                        isCredit ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30'
                      }`}>
                        {isCredit ? (
                          <ArrowUpRight className="h-5 w-5 text-green-600 dark:text-green-400" />
                        ) : (
                          <ArrowDownRight className="h-5 w-5 text-red-600 dark:text-red-400" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          {getCreditTypeIcon(transaction.category)}
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {transaction.description}
                          </p>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {formatDistanceToNow(new Date(transaction.created_at), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold">
                        {formatAmount(transaction.amount)}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Balance: {transaction.balance_after}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
