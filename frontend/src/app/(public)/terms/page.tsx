/**
 * Terms of Service Page
 *
 * Comprehensive terms of service covering:
 * - User agreements and account management
 * - Subscription and billing terms
 * - Acceptable use policies
 * - Intellectual property rights
 * - Disclaimers and limitations of liability
 */

'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

const TABLE_OF_CONTENTS = [
  { id: 'acceptance', title: '1. Acceptance of Terms' },
  { id: 'service', title: '2. Service Description' },
  { id: 'accounts', title: '3. User Accounts' },
  { id: 'billing', title: '4. Subscription & Billing' },
  { id: 'content', title: '5. User Content' },
  { id: 'acceptable-use', title: '6. Acceptable Use' },
  { id: 'ip', title: '7. Intellectual Property' },
  { id: 'disclaimers', title: '8. Disclaimers' },
  { id: 'liability', title: '9. Limitation of Liability' },
  { id: 'termination', title: '10. Termination' },
  { id: 'changes', title: '11. Changes to Terms' },
  { id: 'governing-law', title: '12. Governing Law' },
  { id: 'contact', title: '13. Contact Information' },
]

export default function TermsPage() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-12 text-center"
        >
          <h1 className="text-4xl font-bold text-white">Terms of Service</h1>
          <p className="mt-2 text-gray-400">
            Last Updated: February 9, 2026
          </p>
        </motion.div>

        {/* Table of Contents */}
        <motion.div
          initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="mb-12 rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
        >
          <h2 className="mb-4 text-lg font-semibold text-white">
            Table of Contents
          </h2>
          <nav className="space-y-2">
            {TABLE_OF_CONTENTS.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className="block text-sm text-gray-400 transition-colors hover:text-white"
              >
                {item.title}
              </a>
            ))}
          </nav>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="space-y-12 text-gray-300"
        >
          {/* Section 1 */}
          <section id="acceptance">
            <h2 className="mb-4 text-2xl font-bold text-white">
              1. Acceptance of Terms
            </h2>
            <div className="space-y-4">
              <p>
                By accessing and using Perpetua Flow ("Service"), you accept and
                agree to be bound by these Terms of Service ("Terms"). If you do
                not agree to these Terms, please do not use the Service.
              </p>
              <p>
                These Terms constitute a legally binding agreement between you and
                Perpetua Flow. Your continued use of the Service indicates your
                acceptance of these Terms and any modifications made to them.
              </p>
            </div>
          </section>

          {/* Section 2 */}
          <section id="service">
            <h2 className="mb-4 text-2xl font-bold text-white">
              2. Service Description
            </h2>
            <div className="space-y-4">
              <p>
                Perpetua is a productivity and task management application that
                provides:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Task creation and management with priorities and due dates</li>
                <li>Streak tracking and consistency monitoring</li>
                <li>Focus mode with timer functionality</li>
                <li>Quick notes and idea capture</li>
                <li>Smart reminders and notifications</li>
                <li>Achievement tracking and progress visualization</li>
                <li>AI-powered subtask generation (Pro tier)</li>
                <li>Recurring tasks and advanced analytics (Pro tier)</li>
              </ul>
              <p>
                We reserve the right to modify, suspend, or discontinue any part
                of the Service at any time with reasonable notice to users.
              </p>
            </div>
          </section>

          {/* Section 3 */}
          <section id="accounts">
            <h2 className="mb-4 text-2xl font-bold text-white">
              3. User Accounts
            </h2>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">
                Registration
              </h3>
              <p>
                To use certain features of the Service, you must register for an
                account using Google OAuth. You agree to:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Provide accurate, current, and complete information</li>
                <li>Maintain and update your information as needed</li>
                <li>Maintain the security of your account credentials</li>
                <li>Accept responsibility for all activities under your account</li>
                <li>Notify us immediately of any unauthorized access</li>
              </ul>
              <h3 className="mt-6 text-lg font-semibold text-white">
                Account Security
              </h3>
              <p>
                You are responsible for safeguarding your account. We recommend
                using a strong password and enabling two-factor authentication
                through your Google account. You agree to immediately notify us of
                any security breach or unauthorized use of your account.
              </p>
              <h3 className="mt-6 text-lg font-semibold text-white">
                Account Termination
              </h3>
              <p>
                You may terminate your account at any time through your account
                settings. We may suspend or terminate your account for violation
                of these Terms, with or without notice.
              </p>
            </div>
          </section>

          {/* Section 4 */}
          <section id="billing">
            <h2 className="mb-4 text-2xl font-bold text-white">
              4. Subscription & Billing
            </h2>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Free Tier</h3>
              <p>
                The Free tier provides access to core features including 50 active
                tasks, streak tracking, notes, focus mode, and notifications. No
                credit card is required for the Free tier.
              </p>
              <h3 className="mt-6 text-lg font-semibold text-white">Pro Tier</h3>
              <p>
                The Pro tier is billed monthly at $9/month and includes unlimited
                tasks, AI subtask generation, recurring tasks, analytics, custom
                themes, and priority support.
              </p>
              <h3 className="mt-6 text-lg font-semibold text-white">
                Payment Terms
              </h3>
              <ul className="list-disc space-y-2 pl-6">
                <li>Subscription fees are billed in advance on a monthly basis</li>
                <li>Payments are processed securely through Checkout.com</li>
                <li>Prices are subject to change with 30 days' notice</li>
                <li>You authorize us to charge your payment method for renewal</li>
                <li>Failed payments may result in service suspension</li>
              </ul>
              <h3 className="mt-6 text-lg font-semibold text-white">
                Refund Policy
              </h3>
              <p>
                We offer a 14-day money-back guarantee for first-time Pro
                subscribers. Refunds for subsequent billing cycles are handled on a
                case-by-case basis. Contact support@perpetuaflow.com for refund
                requests.
              </p>
              <h3 className="mt-6 text-lg font-semibold text-white">
                Cancellation
              </h3>
              <p>
                You may cancel your Pro subscription at any time. Your access will
                continue until the end of your current billing period. No partial
                refunds are provided for early cancellation.
              </p>
            </div>
          </section>

          {/* Section 5 */}
          <section id="content">
            <h2 className="mb-4 text-2xl font-bold text-white">
              5. User Content
            </h2>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Ownership</h3>
              <p>
                You retain all ownership rights to the content you create, upload,
                or store on the Service ("User Content"), including tasks, notes,
                and any other data.
              </p>
              <h3 className="mt-6 text-lg font-semibold text-white">
                License Granted to Us
              </h3>
              <p>
                By submitting User Content, you grant us a limited, worldwide,
                non-exclusive license to use, store, and process your content
                solely for the purpose of providing and improving the Service. We
                will never sell your data or use it for advertising purposes.
              </p>
              <h3 className="mt-6 text-lg font-semibold text-white">
                Prohibited Content
              </h3>
              <p>You agree not to create, upload, or share content that:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Is illegal, harmful, or violates any laws</li>
                <li>Infringes on intellectual property rights</li>
                <li>Contains malware, viruses, or malicious code</li>
                <li>
                  Harasses, threatens, or promotes violence against others
                </li>
                <li>Contains spam or unsolicited commercial content</li>
              </ul>
            </div>
          </section>

          {/* Section 6 */}
          <section id="acceptable-use">
            <h2 className="mb-4 text-2xl font-bold text-white">
              6. Acceptable Use
            </h2>
            <div className="space-y-4">
              <p>You agree not to:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>
                  Use the Service for any unlawful purpose or in violation of
                  these Terms
                </li>
                <li>
                  Attempt to gain unauthorized access to any part of the Service
                </li>
                <li>
                  Interfere with or disrupt the Service or servers/networks
                  connected to it
                </li>
                <li>
                  Use automated systems (bots, scrapers) to access the Service
                  without permission
                </li>
                <li>
                  Reverse engineer, decompile, or attempt to extract source code
                </li>
                <li>
                  Resell, rent, or lease access to the Service without
                  authorization
                </li>
                <li>
                  Impersonate any person or entity or misrepresent your
                  affiliation
                </li>
                <li>
                  Transmit any viruses, malware, or other malicious code
                </li>
              </ul>
            </div>
          </section>

          {/* Section 7 */}
          <section id="ip">
            <h2 className="mb-4 text-2xl font-bold text-white">
              7. Intellectual Property
            </h2>
            <div className="space-y-4">
              <p>
                The Service, including all code, design, graphics, and content
                (excluding User Content), is owned by Perpetua Flow and protected
                by copyright, trademark, and other intellectual property laws.
              </p>
              <p>
                Perpetua is an open-source project available on GitHub. The source
                code is licensed under [LICENSE TYPE] and may be used in
                accordance with that license. However, the Perpetua name, logo,
                and branding remain our exclusive property.
              </p>
              <p>
                You may not use our trademarks, logos, or branding without our
                prior written permission.
              </p>
            </div>
          </section>

          {/* Section 8 */}
          <section id="disclaimers">
            <h2 className="mb-4 text-2xl font-bold text-white">
              8. Disclaimers
            </h2>
            <div className="space-y-4">
              <p>
                THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT
                WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT
                NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
                PARTICULAR PURPOSE, NON-INFRINGEMENT, OR THAT THE SERVICE WILL BE
                UNINTERRUPTED, SECURE, OR ERROR-FREE.
              </p>
              <p>
                We do not warrant that:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>The Service will meet your specific requirements</li>
                <li>The Service will be uninterrupted or error-free</li>
                <li>Any errors or defects will be corrected</li>
                <li>The Service is free from viruses or harmful components</li>
                <li>
                  Any data, including User Content, will not be lost or corrupted
                </li>
              </ul>
              <p>
                You acknowledge that you use the Service at your own risk.
              </p>
            </div>
          </section>

          {/* Section 9 */}
          <section id="liability">
            <h2 className="mb-4 text-2xl font-bold text-white">
              9. Limitation of Liability
            </h2>
            <div className="space-y-4">
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, PERPETUA FLOW SHALL NOT BE
                LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR
                PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, REVENUE, DATA, OR USE,
                ARISING OUT OF OR RELATED TO THESE TERMS OR THE SERVICE, WHETHER
                BASED ON WARRANTY, CONTRACT, TORT, OR ANY OTHER LEGAL THEORY.
              </p>
              <p>
                OUR TOTAL LIABILITY TO YOU FOR ANY CLAIMS ARISING OUT OF OR
                RELATED TO THESE TERMS OR THE SERVICE SHALL NOT EXCEED THE AMOUNT
                YOU PAID US IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM, OR $100
                USD, WHICHEVER IS GREATER.
              </p>
              <p>
                Some jurisdictions do not allow the exclusion or limitation of
                certain warranties or damages, so some of the above limitations
                may not apply to you.
              </p>
            </div>
          </section>

          {/* Section 10 */}
          <section id="termination">
            <h2 className="mb-4 text-2xl font-bold text-white">
              10. Termination
            </h2>
            <div className="space-y-4">
              <p>
                We reserve the right to suspend or terminate your access to the
                Service at any time, with or without cause, with or without
                notice, including for:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Violation of these Terms</li>
                <li>Fraudulent, abusive, or illegal activity</li>
                <li>Extended periods of inactivity</li>
                <li>Requests by law enforcement or other government agencies</li>
              </ul>
              <p>
                Upon termination, your right to use the Service will immediately
                cease. We may delete your account and User Content, though we will
                make reasonable efforts to provide you with an opportunity to
                export your data before deletion.
              </p>
              <p>
                Sections of these Terms that by their nature should survive
                termination will survive, including ownership provisions,
                warranty disclaimers, and limitations of liability.
              </p>
            </div>
          </section>

          {/* Section 11 */}
          <section id="changes">
            <h2 className="mb-4 text-2xl font-bold text-white">
              11. Changes to Terms
            </h2>
            <div className="space-y-4">
              <p>
                We may modify these Terms at any time. When we make material
                changes, we will notify you by:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Posting a notice on the Service</li>
                <li>Sending an email to the address associated with your account</li>
                <li>Updating the "Last Updated" date at the top of this page</li>
              </ul>
              <p>
                Your continued use of the Service after the effective date of the
                revised Terms constitutes your acceptance of the changes. If you
                do not agree to the new Terms, you must stop using the Service.
              </p>
            </div>
          </section>

          {/* Section 12 */}
          <section id="governing-law">
            <h2 className="mb-4 text-2xl font-bold text-white">
              12. Governing Law
            </h2>
            <div className="space-y-4">
              <p>
                These Terms are governed by and construed in accordance with the
                laws of [YOUR JURISDICTION], without regard to its conflict of law
                principles.
              </p>
              <p>
                Any disputes arising out of or related to these Terms or the
                Service shall be resolved through binding arbitration in
                accordance with the rules of [ARBITRATION BODY], except that
                either party may seek injunctive relief in court to prevent
                infringement of intellectual property rights.
              </p>
              <p>
                You agree to waive any right to a jury trial or to participate in
                a class action lawsuit or class-wide arbitration.
              </p>
            </div>
          </section>

          {/* Section 13 */}
          <section id="contact">
            <h2 className="mb-4 text-2xl font-bold text-white">
              13. Contact Information
            </h2>
            <div className="space-y-4">
              <p>
                If you have any questions about these Terms, please contact us at:
              </p>
              <div className="rounded-lg border border-white/10 bg-white/5 p-4">
                <p className="font-medium text-white">Perpetua Flow</p>
                <p>Email: support@perpetuaflow.com</p>
                <p>
                  Contact Form:{' '}
                  <Link
                    href="/contact"
                    className="text-blue-400 hover:underline"
                  >
                    /contact
                  </Link>
                </p>
              </div>
            </div>
          </section>

          {/* Footer Note */}
          <div className="border-t border-white/10 pt-8 text-center text-sm text-gray-500">
            <p>
              By using Perpetua, you acknowledge that you have read, understood,
              and agree to be bound by these Terms of Service.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
