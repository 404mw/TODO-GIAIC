/**
 * Terms of Service Page
 *
 * Legal document outlining the terms and conditions for using Perpetua Flow.
 * Last Updated: February 8, 2026
 */

'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

export default function TermsPage() {
  const shouldReduceMotion = useReducedMotion()

  const fadeIn = shouldReduceMotion
    ? {}
    : {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.4 },
      }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 py-24">
        {/* Background gradient */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -left-1/4 top-0 h-[500px] w-[500px] rounded-full bg-blue-500/10 blur-3xl" />
          <div className="absolute -right-1/4 top-1/4 h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-3xl" />
        </div>

        <motion.div {...fadeIn} className="relative mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold text-white sm:text-5xl">
            Terms of Service
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-400">
            Please read these terms carefully before using Perpetua Flow.
          </p>
          <p className="mt-4 text-sm text-gray-500">
            Last Updated: February 8, 2026
          </p>
        </motion.div>
      </section>

      {/* Content Sections */}
      <section className="px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-8">
          {/* Introduction */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.1 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">1. Introduction and Acceptance</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Welcome to Perpetua Flow ("Service", "we", "us", or "our"). By accessing or using our task management application, you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, please do not use the Service.
              </p>
              <p>
                These Terms constitute a legally binding agreement between you and Perpetua Flow. We reserve the right to modify these Terms at any time, and will notify users of material changes via email or in-app notification.
              </p>
            </div>
          </motion.div>

          {/* Service Description */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.15 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">2. Description of Service</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Perpetua Flow is a productivity and task management platform that helps users organize tasks, track habits, and build consistency through features including:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Task creation and management with subtasks</li>
                <li>Consistency streaks with grace days</li>
                <li>Focus mode timers for productive work sessions</li>
                <li>Browser notifications and reminders</li>
                <li>AI-powered subtask generation (Pro tier)</li>
                <li>Achievement system and productivity analytics</li>
                <li>Quick notes and voice recording</li>
              </ul>
              <p>
                The Service is provided on a subscription basis with both free and paid tiers, as described in Section 4.
              </p>
            </div>
          </motion.div>

          {/* User Accounts */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.2 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">3. User Accounts and Authentication</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Account Creation:</strong> Perpetua Flow uses Google OAuth for authentication. By signing in, you authorize us to access your Google account name, email address, and profile picture for the purpose of account creation and identification.
              </p>
              <p>
                <strong>Account Security:</strong> You are responsible for maintaining the security of your Google account. We are not liable for any loss or damage arising from unauthorized access to your account.
              </p>
              <p>
                <strong>Account Termination:</strong> You may delete your account at any time through the application settings. Upon account deletion, all your data will be permanently removed from our systems within 30 days, except as required by law.
              </p>
              <p>
                <strong>Prohibited Conduct:</strong> You agree not to use the Service to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Violate any applicable laws or regulations</li>
                <li>Infringe on intellectual property rights</li>
                <li>Harass, abuse, or harm other users</li>
                <li>Attempt to gain unauthorized access to the Service</li>
                <li>Upload malicious code, viruses, or malware</li>
                <li>Use the Service for any automated or commercial purpose without permission</li>
              </ul>
            </div>
          </motion.div>

          {/* Subscription & Billing */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.25 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">4. Subscription and Billing</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Free Tier:</strong> The free tier includes:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Up to 50 active tasks</li>
                <li>Up to 10 notes</li>
                <li>5 AI credits daily</li>
                <li>Basic achievements and streak tracking</li>
                <li>Focus mode and browser notifications</li>
              </ul>
              <p>
                <strong>Pro Tier:</strong> The Pro subscription ($9/month) includes:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Unlimited tasks and notes</li>
                <li>50 daily AI credits + 100 monthly subscription credits</li>
                <li>AI-powered subtask generation</li>
                <li>All achievements unlocked</li>
                <li>Priority customer support</li>
              </ul>
              <p>
                <strong>Billing:</strong> Pro subscriptions are billed monthly. You authorize us to charge your payment method on a recurring basis. You may cancel your subscription at any time, and you will retain Pro access until the end of your billing period.
              </p>
              <p>
                <strong>Refunds:</strong> We do not offer refunds for partial months. If you downgrade from Pro to Free, your account will be subject to free tier limits, and excess tasks/notes will remain accessible but you will not be able to create new items beyond the free limits until you reduce your total count.
              </p>
              <p>
                <strong>Price Changes:</strong> We reserve the right to change subscription pricing with 30 days' notice. Existing subscribers will be grandfathered at their current rate for at least 6 months.
              </p>
            </div>
          </motion.div>

          {/* AI Features */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.3 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">5. AI Features and Disclaimer</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>AI-Generated Content:</strong> Perpetua Flow offers AI-powered subtask generation to help break down complex tasks. This feature uses third-party AI services to analyze your task descriptions and generate suggestions.
              </p>
              <p>
                <strong>No Warranty:</strong> AI-generated suggestions are provided "as is" without warranty of any kind. We do not guarantee the accuracy, completeness, or usefulness of AI-generated content. You are solely responsible for reviewing and approving any AI suggestions before using them.
              </p>
              <p>
                <strong>Credit System:</strong> AI features consume credits. Credits are allocated based on your subscription tier and reset according to defined schedules (daily, monthly). Unused credits do not roll over except for subscription credits, which have a carryover limit.
              </p>
            </div>
          </motion.div>

          {/* Service Availability */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.35 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">6. Service Availability and Changes</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Uptime:</strong> We strive to maintain 99.9% uptime, but we do not guarantee uninterrupted access to the Service. We may perform scheduled maintenance with advance notice when possible.
              </p>
              <p>
                <strong>Service Changes:</strong> We reserve the right to modify, suspend, or discontinue any feature of the Service at any time with reasonable notice. We will not be liable for any modification, suspension, or discontinuance of the Service.
              </p>
              <p>
                <strong>Beta Features:</strong> We may offer beta or experimental features. These features are provided "as is" and may be changed or removed without notice.
              </p>
            </div>
          </motion.div>

          {/* Termination */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.4 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">7. Termination Rights</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Termination by You:</strong> You may terminate your account at any time by deleting it through the application settings. Upon termination, your subscription will be cancelled and your data will be deleted as described in our Privacy Policy.
              </p>
              <p>
                <strong>Termination by Us:</strong> We reserve the right to suspend or terminate your account if:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>You violate these Terms of Service</li>
                <li>Your account is used for fraudulent or illegal activity</li>
                <li>Your payment method fails and you do not provide a valid alternative</li>
                <li>We are required to do so by law</li>
              </ul>
              <p>
                We will provide notice of termination when possible, but we reserve the right to terminate accounts immediately for serious violations.
              </p>
            </div>
          </motion.div>

          {/* Data Privacy */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.45 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">8. Data Privacy and GDPR Compliance</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Your privacy is important to us. Our collection, use, and protection of your personal data is governed by our{' '}
                <Link href="/privacy" className="text-blue-400 hover:text-blue-300 underline">
                  Privacy Policy
                </Link>
                , which is incorporated into these Terms by reference.
              </p>
              <p>
                <strong>Your Rights:</strong> Under GDPR and applicable data protection laws, you have the right to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Access your personal data</li>
                <li>Rectify inaccurate data</li>
                <li>Request deletion of your data ("right to be forgotten")</li>
                <li>Export your data in a portable format</li>
                <li>Object to processing of your data</li>
                <li>Withdraw consent at any time</li>
              </ul>
              <p>
                To exercise these rights, please contact us at the email provided in Section 13.
              </p>
            </div>
          </motion.div>

          {/* Intellectual Property */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.5 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">9. Intellectual Property</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Our Rights:</strong> Perpetua Flow, including its design, features, functionality, and content (excluding user-generated content), is owned by us and protected by copyright, trademark, and other intellectual property laws.
              </p>
              <p>
                <strong>Your Content:</strong> You retain all rights to the content you create using the Service (tasks, notes, etc.). By using the Service, you grant us a limited license to store, display, and process your content solely for the purpose of providing the Service to you.
              </p>
              <p>
                <strong>Restrictions:</strong> You may not:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Copy, modify, or create derivative works of the Service</li>
                <li>Reverse engineer or attempt to extract source code</li>
                <li>Remove any copyright or proprietary notices</li>
                <li>Use our trademarks without permission</li>
              </ul>
            </div>
          </motion.div>

          {/* Limitation of Liability */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.55 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">10. Limitation of Liability</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>AS-IS Basis:</strong> The Service is provided "as is" and "as available" without warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.
              </p>
              <p>
                <strong>Limitation:</strong> To the maximum extent permitted by law, Perpetua Flow shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, whether in an action in contract, tort, or otherwise, arising from your use of the Service.
              </p>
              <p>
                <strong>Maximum Liability:</strong> Our total liability to you for any claims arising from these Terms or your use of the Service shall not exceed the amount you paid us in the 12 months preceding the claim, or $100, whichever is greater.
              </p>
              <p>
                Some jurisdictions do not allow the exclusion or limitation of certain warranties or liabilities, so some of the above limitations may not apply to you.
              </p>
            </div>
          </motion.div>

          {/* Dispute Resolution */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.6 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">11. Dispute Resolution</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Informal Resolution:</strong> If you have a dispute with us, please contact us first at the email address below. We will work with you in good faith to resolve the issue.
              </p>
              <p>
                <strong>Governing Law:</strong> These Terms shall be governed by and construed in accordance with the laws of the jurisdiction in which our company is registered, without regard to its conflict of law provisions.
              </p>
              <p>
                <strong>Arbitration:</strong> Any disputes arising from these Terms or your use of the Service shall be resolved through binding arbitration, except that either party may seek injunctive relief in court for intellectual property infringement or unauthorized access.
              </p>
            </div>
          </motion.div>

          {/* General Provisions */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.65 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">12. General Provisions</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Entire Agreement:</strong> These Terms, together with our Privacy Policy, constitute the entire agreement between you and Perpetua Flow regarding the Service.
              </p>
              <p>
                <strong>Severability:</strong> If any provision of these Terms is found to be unenforceable, the remaining provisions will remain in full effect.
              </p>
              <p>
                <strong>Waiver:</strong> Our failure to enforce any right or provision of these Terms will not be considered a waiver of those rights.
              </p>
              <p>
                <strong>Assignment:</strong> You may not assign or transfer these Terms without our prior written consent. We may assign these Terms without restriction.
              </p>
            </div>
          </motion.div>

          {/* Contact Information */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.7 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">13. Contact Information</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                If you have any questions about these Terms of Service, please contact us:
              </p>
              <ul className="space-y-2 ml-4">
                <li>
                  <strong>Email:</strong>{' '}
                  <a href="mailto:legal@perpetuaflow.com" className="text-blue-400 hover:text-blue-300 underline">
                    legal@perpetuaflow.com
                  </a>
                </li>
                <li>
                  <strong>Contact Form:</strong>{' '}
                  <Link href="/contact" className="text-blue-400 hover:text-blue-300 underline">
                    perpetuaflow.com/contact
                  </Link>
                </li>
              </ul>
              <p className="mt-4 text-sm text-gray-500">
                Last Updated: February 8, 2026
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-24">
        <motion.div
          {...fadeIn}
          transition={{ delay: 0.75 }}
          className="mx-auto max-w-4xl rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-12 text-center backdrop-blur-sm"
        >
          <h2 className="text-3xl font-bold text-white">
            Ready to get started?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-gray-300">
            By using Perpetua Flow, you agree to these Terms of Service and our Privacy Policy.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link
              href="/dashboard"
              className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
            >
              Get Started Free
            </Link>
            <Link
              href="/privacy"
              className="rounded-lg border border-white/20 bg-white/5 px-6 py-3 font-medium text-white transition-colors hover:bg-white/10"
            >
              Privacy Policy
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  )
}
