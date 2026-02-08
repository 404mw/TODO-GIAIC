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
    description: 'Perfect for getting started',
    price: '$0',
    period: 'forever',
    features: [
      'Up to 50 active tasks',
      'Up to 10 notes',
      '5 AI kickstart credits',
      'Basic achievements',
      'Streak tracking',
      'Focus mode',
      'Browser notifications',
      'Up to 4 subtasks per task',
    ],
    cta: 'Get Started Free',
    ctaLink: '/dashboard/tasks',
    highlighted: false,
  },
  {
    name: 'Pro',
    description: 'For power users',
    price: '$9',
    period: 'per month',
    features: [
      'Unlimited tasks & notes',
      '10 daily + 100 monthly AI credits',
      'All achievements unlocked',
      'AI-powered subtask generation',
      'Recurring tasks',
      'Priority support',
      'Up to 10 subtasks per task',
      'Extended task descriptions (2,000 chars)',
    ],
    cta: 'Upgrade to Pro',
    ctaLink: '/dashboard/tasks',
    highlighted: true,
  },
]

const FAQS = [
  {
    question: 'Can I switch plans later?',
    answer:
      "Yes! You can upgrade from Free to Pro at any time and start enjoying Pro benefits immediately. If you cancel your Pro subscription, you'll keep Pro access until the end of your billing period, then automatically return to the Free tier.",
  },
  {
    question: 'Is the free tier really free forever?',
    answer:
      "Yes! Our Free tier is completely free forever, with no credit card required. You get 50 active tasks, 10 notes, 5 AI kickstart credits to get started, and can earn achievements to unlock even more. We believe everyone deserves powerful productivity tools.",
  },
  {
    question: 'What happens to my data if I downgrade?',
    answer:
      "Your data is always safe! If you exceed Free tier limits (50 tasks, 10 notes), you can still view and edit existing items, but you'll need to complete or delete some before creating new ones. Consider unlocking achievements to increase your limits without upgrading.",
  },
  {
    question: 'How do AI credits work?',
    answer:
      "AI credits power features like subtask generation and note-to-task conversion. Free users get 5 kickstart credits (never expire). Pro users get 10 daily credits (reset at midnight UTC) plus 100 monthly subscription credits (up to 50 carry over each month). Credits are used in this order: daily, subscription, purchased, then kickstart.",
  },
  {
    question: 'How does the AI sub-task generation work?',
    answer:
      'Our AI analyzes your task description and automatically suggests relevant sub-tasks to help break down complex projects. You can review and customize the suggestions before adding them.',
  },
]

const FEATURE_COMPARISON = [
  {
    category: 'Tasks & Organization',
    features: [
      { name: 'Active tasks limit', free: '50 tasks', pro: '200+ tasks*' },
      { name: 'Subtasks per task', free: '4 subtasks', pro: '10 subtasks' },
      { name: 'Task description length', free: '1,000 characters', pro: '2,000 characters' },
      { name: 'Recurring tasks', free: '✗', pro: '✓' },
    ],
  },
  {
    category: 'Notes & AI Features',
    features: [
      { name: 'Notes limit', free: '10 notes', pro: '25+ notes*' },
      { name: 'AI credits (kickstart)', free: '5 credits', pro: '5 credits' },
      { name: 'AI credits (daily)', free: '—', pro: '10 credits/day*' },
      { name: 'AI credits (monthly)', free: '—', pro: '100 credits/month' },
      { name: 'AI subtask generation', free: '✗', pro: '✓' },
      { name: 'Note-to-task conversion', free: 'Manual', pro: 'AI-powered' },
    ],
  },
  {
    category: 'Productivity & Gamification',
    features: [
      { name: 'Achievements', free: 'View only', pro: 'Unlock perks*' },
      { name: 'Streak tracking', free: '✓', pro: '✓' },
      { name: 'Grace days', free: '✓', pro: '✓' },
      { name: 'Focus mode', free: '✓', pro: '✓' },
    ],
  },
  {
    category: 'Support & Priority',
    features: [
      { name: 'Community support', free: '✓', pro: '✓' },
      { name: 'Priority support', free: '✗', pro: '✓' },
      { name: 'Feature requests', free: 'Standard queue', pro: 'Priority queue' },
    ],
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
            Start free forever, or unlock Pro features when you need more power.
            No credit card required. Cancel Pro anytime.
          </p>
        </motion.div>
      </section>

      {/* Free Forever Banner */}
      <section className="pb-8">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="relative overflow-hidden rounded-2xl border border-green-500/30 bg-gradient-to-r from-green-500/10 to-blue-500/10 p-6 backdrop-blur-sm"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-blue-500/5" />
            <div className="relative z-10 flex flex-col items-center gap-3 text-center sm:flex-row sm:text-left">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-green-500/20">
                <svg
                  className="h-6 w-6 text-green-400"
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
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white">
                  Free Tier Available Forever
                </h3>
                <p className="text-sm text-gray-300">
                  No credit card required. Start with 50 tasks, 10 notes, and 5
                  AI credits. Unlock achievements to increase your limits.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
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
                  <p className="mt-2 text-gray-400">{plan.description}</p>
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
          <motion.div
            initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-white">Compare features</h2>
            <p className="mx-auto mt-4 max-w-2xl text-gray-400">
              See exactly what&apos;s included in each plan
            </p>
          </motion.div>

          <div className="mt-12 overflow-x-auto">
            <div className="inline-block min-w-full align-middle">
              <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm">
                {FEATURE_COMPARISON.map((categoryGroup) => (
                  <div key={categoryGroup.category}>
                    <div className="border-b border-white/10 bg-white/5 px-6 py-4">
                      <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
                        {categoryGroup.category}
                      </h3>
                    </div>
                    {categoryGroup.features.map((feature, featureIndex) => (
                      <motion.div
                        key={feature.name}
                        initial={shouldReduceMotion ? {} : { opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        transition={{ duration: 0.3, delay: featureIndex * 0.05 }}
                        viewport={{ once: true }}
                        className="grid grid-cols-1 gap-4 border-b border-white/5 px-6 py-4 last:border-b-0 sm:grid-cols-3 sm:gap-8"
                      >
                        <div className="font-medium text-gray-300 sm:col-span-1">
                          {feature.name}
                        </div>
                        <div className="flex items-center gap-2 text-gray-400 sm:justify-center">
                          <span className="text-xs font-medium uppercase text-gray-500 sm:hidden">
                            Free:
                          </span>
                          <span
                            className={
                              feature.free === '✓'
                                ? 'text-green-400'
                                : feature.free === '✗'
                                  ? 'text-gray-600'
                                  : ''
                            }
                          >
                            {feature.free}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-300 sm:justify-center">
                          <span className="text-xs font-medium uppercase text-gray-500 sm:hidden">
                            Pro:
                          </span>
                          <span
                            className={
                              feature.pro === '✓'
                                ? 'text-green-400 font-semibold'
                                : feature.pro === '✗'
                                  ? 'text-gray-600'
                                  : 'font-semibold'
                            }
                          >
                            {feature.pro}
                          </span>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <motion.p
            initial={shouldReduceMotion ? {} : { opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            viewport={{ once: true }}
            className="mt-6 text-center text-sm text-gray-500"
          >
            * Pro users can unlock achievements to increase task limits (up to
            +90 tasks), note limits (up to +10 notes), and daily credits (up to
            +7 credits/day).
          </motion.p>
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
