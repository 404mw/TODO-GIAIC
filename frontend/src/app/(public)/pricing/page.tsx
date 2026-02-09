/**
 * Pricing Page (T155)
 * Phase 13 - Public Pages
 *
 * Displays pricing tiers with:
 * - Free tier with basic features
 * - Pro tier with advanced features
 * - Feature comparison table
 * - FAQ section
 *
 * Uses shared layout.tsx for navigation and footer
 */

'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

const PLANS = [
  {
    name: 'Free',
    message: 'Perfect for getting started',
    price: '$0',
    period: 'forever',
    features: [
      'Up to 50 active tasks',
      'Basic task management',
      'Streak tracking',
      'Quick notes',
      'Focus mode timer',
      'Browser notifications',
    ],
    cta: 'Get Started Free',
    ctaLink: '/dashboard/tasks',
    highlighted: false,
  },
  {
    name: 'Pro',
    message: 'For power users',
    price: '$9',
    period: 'per month',
    features: [
      'Unlimited tasks',
      'AI-powered sub-task generation',
      'Recurring tasks',
      'Advanced analytics',
      'Custom themes',
      'Priority support',
      'Cloud sync across devices',
      'Export & backup',
    ],
    cta: 'Start 14-Day Trial',
    ctaLink: '/dashboard/tasks',
    highlighted: true,
  },
]

const COMPARISON_FEATURES = [
  { name: 'Active Tasks', free: '50 tasks', pro: 'Unlimited' },
  { name: 'AI Sub-task Generation', free: false, pro: true },
  { name: 'Recurring Tasks', free: false, pro: true },
  { name: 'Streak Tracking', free: true, pro: true },
  { name: 'Focus Mode', free: true, pro: true },
  { name: 'Quick Notes', free: true, pro: true },
  { name: 'Smart Reminders', free: true, pro: true },
  { name: 'Achievements', free: true, pro: true },
  { name: 'Analytics Dashboard', free: false, pro: true },
  { name: 'Custom Themes', free: false, pro: true },
  { name: 'Cloud Sync', free: 'Basic', pro: 'Advanced' },
  { name: 'Data Export', free: false, pro: true },
  { name: 'Support', free: 'Community', pro: 'Priority' },
]

const FAQS = [
  {
    question: 'Can I switch plans later?',
    answer:
      "Yes! You can upgrade or downgrade your plan at any time. When upgrading, you'll be charged the prorated difference. When downgrading, the difference will be credited to your account.",
  },
  {
    question: 'What happens to my data if I downgrade?',
    answer:
      "Your data is always safe. If you exceed the free tier limits, you'll still have access to view and edit your existing tasks, but you won't be able to create new ones until you're within the limits.",
  },
  {
    question: 'Is there a free trial for Pro?',
    answer:
      'Yes! Pro comes with a 14-day free trial. No credit card required to start. You can explore all Pro features risk-free before deciding to subscribe.',
  },
  {
    question: 'How does the AI sub-task generation work?',
    answer:
      'Our AI analyzes your task description and automatically suggests relevant sub-tasks to help break down complex projects. You can review and customize the suggestions before adding them.',
  },
  {
    question: 'How do I upgrade from Free to Pro?',
    answer:
      'Upgrading is easy! Just go to your account settings and click "Upgrade to Pro". You\'ll be redirected to our secure payment page powered by Checkout.com. Your Pro features will be activated immediately after payment.',
  },
  {
    question: 'Can I cancel anytime?',
    answer:
      'Absolutely! There are no long-term commitments. You can cancel your Pro subscription at any time from your account settings. You\'ll retain Pro access until the end of your current billing period.',
  },
  {
    question: 'Do you offer refunds?',
    answer:
      'We offer a full refund within 14 days of your initial purchase if you\'re not satisfied with Pro. For subsequent billing cycles, refunds are handled on a case-by-case basis. Contact our support team to discuss your situation.',
  },
  {
    question: 'What payment methods do you accept?',
    answer:
      'We accept all major credit cards (Visa, Mastercard, American Express, Discover) and debit cards through our payment processor, Checkout.com. All transactions are secure and encrypted.',
  },
  {
    question: 'Is my data secure?',
    answer:
      'Yes! We take security seriously. All data is encrypted in transit and at rest. We use industry-standard security practices and never sell your data to third parties. For more details, read our Privacy Policy.',
  },
]

export default function PricingPage() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <div className="min-h-screen">
      {/* Header */}
      <section className="py-16">
        <motion.div
          initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8"
        >
          <h1 className="text-4xl font-bold text-white">
            Simple, transparent pricing
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-400">
            Start free and upgrade when you need more power. No hidden fees,
            cancel anytime.
          </p>
        </motion.div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-2">
            {PLANS.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className={[
                  'relative overflow-hidden rounded-2xl p-8 backdrop-blur-sm',
                  plan.highlighted
                    ? 'border-2 border-blue-500/50 bg-white/10'
                    : 'border border-white/10 bg-white/5',
                ].join(' ')}
              >
                {/* Gradient decoration for highlighted plan */}
                {plan.highlighted && (
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10" />
                )}

                <div className="relative z-10">
                  {plan.highlighted && (
                    <div className="mb-4">
                      <span className="rounded-full bg-blue-500/20 px-3 py-1 text-sm font-medium text-blue-300">
                        Most Popular
                      </span>
                    </div>
                  )}
                  <h2 className="text-2xl font-bold text-white">{plan.name}</h2>
                  <p className="mt-2 text-gray-400">{plan.message}</p>
                  <div className="mt-6">
                    <span className="text-4xl font-bold text-white">
                      {plan.price}
                    </span>
                    <span className="text-gray-400"> /{plan.period}</span>
                  </div>
                  <ul className="mt-8 space-y-4">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-3">
                        <svg
                          className="h-5 w-5 flex-shrink-0 text-green-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        <span className="text-gray-300">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Link
                    href={plan.ctaLink}
                    className={[
                      'mt-8 block w-full rounded-lg px-4 py-3 text-center text-sm font-medium transition-all',
                      plan.highlighted
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700'
                        : 'border border-white/20 text-white hover:bg-white/10',
                    ].join(' ')}
                  >
                    {plan.cta}
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="border-t border-white/10 py-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <motion.h2
            initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
            className="text-center text-3xl font-bold text-white mb-12"
          >
            Compare Plans
          </motion.h2>

          {/* Desktop Table */}
          <div className="hidden md:block">
            <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    <th className="px-6 py-4 text-left text-sm font-semibold text-white">
                      Feature
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-white">
                      Free
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-white">
                      Pro
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARISON_FEATURES.map((feature, index) => (
                    <tr
                      key={feature.name}
                      className={index % 2 === 0 ? 'bg-white/5' : ''}
                    >
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {feature.name}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {typeof feature.free === 'boolean' ? (
                          feature.free ? (
                            <svg
                              className="mx-auto h-5 w-5 text-green-400"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          ) : (
                            <svg
                              className="mx-auto h-5 w-5 text-gray-600"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                              />
                            </svg>
                          )
                        ) : (
                          <span className="text-sm text-gray-400">
                            {feature.free}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {typeof feature.pro === 'boolean' ? (
                          feature.pro ? (
                            <svg
                              className="mx-auto h-5 w-5 text-green-400"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          ) : (
                            <svg
                              className="mx-auto h-5 w-5 text-gray-600"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                              />
                            </svg>
                          )
                        ) : (
                          <span className="text-sm text-gray-300 font-medium">
                            {feature.pro}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mobile Accordion */}
          <div className="md:hidden space-y-4">
            {COMPARISON_FEATURES.map((feature) => (
              <div
                key={feature.name}
                className="rounded-lg border border-white/10 bg-white/5 p-4 backdrop-blur-sm"
              >
                <h3 className="font-semibold text-white mb-3">
                  {feature.name}
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Free</div>
                    <div className="flex items-center gap-2">
                      {typeof feature.free === 'boolean' ? (
                        feature.free ? (
                          <svg
                            className="h-4 w-4 text-green-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="h-4 w-4 text-gray-600"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        )
                      ) : (
                        <span className="text-sm text-gray-400">
                          {feature.free}
                        </span>
                      )}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Pro</div>
                    <div className="flex items-center gap-2">
                      {typeof feature.pro === 'boolean' ? (
                        feature.pro ? (
                          <svg
                            className="h-4 w-4 text-green-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="h-4 w-4 text-gray-600"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        )
                      ) : (
                        <span className="text-sm text-gray-300 font-medium">
                          {feature.pro}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="border-t border-white/10 bg-white/5 py-24">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <motion.h2
            initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
            className="text-center text-3xl font-bold text-white"
          >
            Frequently asked questions
          </motion.h2>
          <div className="mt-12 space-y-8">
            {FAQS.map((faq, index) => (
              <motion.div
                key={faq.question}
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
                viewport={{ once: true }}
              >
                <h3 className="text-lg font-semibold text-white">
                  {faq.question}
                </h3>
                <p className="mt-2 text-gray-400">{faq.answer}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
