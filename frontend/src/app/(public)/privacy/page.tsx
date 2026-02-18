/**
 * Privacy Policy Page
 *
 * Comprehensive privacy policy covering:
 * - Data collection and usage
 * - Third-party services
 * - User rights (GDPR, CCPA)
 * - Security measures
 * - Cookie policies
 */

'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

const TABLE_OF_CONTENTS = [
  { id: 'introduction', title: '1. Introduction' },
  { id: 'information-we-collect', title: '2. Information We Collect' },
  { id: 'how-we-use', title: '3. How We Use Information' },
  { id: 'data-storage', title: '4. Data Storage & Security' },
  { id: 'third-party', title: '5. Third-Party Services' },
  { id: 'cookies', title: '6. Cookies & Tracking' },
  { id: 'your-rights', title: '7. Your Rights (GDPR)' },
  { id: 'children', title: '8. Children\'s Privacy' },
  { id: 'open-source', title: '9. Open Source Notice' },
  { id: 'data-sharing', title: '10. Data Sharing' },
  { id: 'california', title: '11. California Privacy Rights (CCPA)' },
  { id: 'changes', title: '12. Changes to Policy' },
  { id: 'contact', title: '13. Contact Us' },
]

export default function PrivacyPage() {
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
          <h1 className="text-4xl font-bold text-white">Privacy Policy</h1>
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
          <section id="introduction">
            <h2 className="mb-4 text-2xl font-bold text-white">
              1. Introduction
            </h2>
            <div className="space-y-4">
              <p>
                Welcome to Perpetua Flow ("we," "our," or "us"). We are committed
                to protecting your privacy and being transparent about the data we
                collect, how we use it, and your rights regarding your personal
                information.
              </p>
              <p>
                This Privacy Policy explains how we collect, use, disclose, and
                safeguard your information when you use our productivity and task
                management application ("Service"). By using the Service, you
                consent to the data practices described in this policy.
              </p>
              <p>
                If you do not agree with this policy, please discontinue use of
                the Service immediately.
              </p>
            </div>
          </section>

          {/* Section 2 */}
          <section id="information-we-collect">
            <h2 className="mb-4 text-2xl font-bold text-white">
              2. Information We Collect
            </h2>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">
                Account Information
              </h3>
              <p>When you sign up using Google OAuth, we collect:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Email address</li>
                <li>Name</li>
                <li>Profile picture (if provided via Google)</li>
                <li>Google user ID</li>
              </ul>

              <h3 className="mt-6 text-lg font-semibold text-white">
                Usage Data
              </h3>
              <p>We automatically collect certain information when you use the Service:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Device information (type, operating system, browser)</li>
                <li>IP address and approximate location</li>
                <li>Pages visited and features used</li>
                <li>Time and date of access</li>
                <li>Referring/exit pages</li>
                <li>Clicks, scrolls, and other interaction data</li>
              </ul>

              <h3 className="mt-6 text-lg font-semibold text-white">
                User Content
              </h3>
              <p>We store the content you create on the Service:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Tasks, subtasks, and descriptions</li>
                <li>Notes and quick captures</li>
                <li>User preferences and settings</li>
                <li>Focus session data and achievements</li>
                <li>Reminder configurations</li>
              </ul>

              <h3 className="mt-6 text-lg font-semibold text-white">
                Payment Information
              </h3>
              <p>
                If you subscribe to Pro, we collect billing information through
                our payment processor, Checkout.com. We do not store your full
                credit card details on our servers—only the last 4 digits and card
                type for reference.
              </p>
            </div>
          </section>

          {/* Section 3 */}
          <section id="how-we-use">
            <h2 className="mb-4 text-2xl font-bold text-white">
              3. How We Use Information
            </h2>
            <div className="space-y-4">
              <p>We use your information to:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>
                  <strong>Provide the Service:</strong> Create and manage your
                  account, store your tasks and notes, deliver features like
                  reminders and achievements
                </li>
                <li>
                  <strong>Process Payments:</strong> Handle subscription billing
                  and credit purchases
                </li>
                <li>
                  <strong>Improve the Service:</strong> Analyze usage patterns,
                  fix bugs, develop new features
                </li>
                <li>
                  <strong>Communicate:</strong> Send service updates, respond to
                  support requests, notify you of changes
                </li>
                <li>
                  <strong>Security:</strong> Detect and prevent fraud, abuse, and
                  security threats
                </li>
                <li>
                  <strong>Legal Compliance:</strong> Comply with applicable laws
                  and regulations
                </li>
              </ul>
              <p className="mt-4 font-semibold text-emerald-400">
                We will never sell your data to third parties or use it for
                advertising purposes.
              </p>
            </div>
          </section>

          {/* Section 4 */}
          <section id="data-storage">
            <h2 className="mb-4 text-2xl font-bold text-white">
              4. Data Storage & Security
            </h2>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Storage Location</h3>
              <p>
                Your data is stored on secure servers in Frankfurt. We use
                industry-standard encryption for data in transit (TLS/SSL) and at
                rest (AES-256).
              </p>

              <h3 className="mt-6 text-lg font-semibold text-white">
                Security Measures
              </h3>
              <ul className="list-disc space-y-2 pl-6">
                <li>Encrypted connections (HTTPS everywhere)</li>
                <li>Encrypted database storage</li>
                <li>Regular security audits and penetration testing</li>
                <li>Access controls and authentication requirements</li>
                <li>Automated backups and disaster recovery plans</li>
                <li>Security monitoring and incident response procedures</li>
              </ul>

              <h3 className="mt-6 text-lg font-semibold text-white">
                Data Retention
              </h3>
              <p>
                We retain your data for as long as your account is active. If you
                delete your account, we will delete your personal information
                within 30 days, except where we are required to retain it for
                legal, security, or fraud prevention purposes.
              </p>
              <p>
                Anonymized usage data may be retained indefinitely for analytics
                and service improvement.
              </p>
            </div>
          </section>

          {/* Section 5 */}
          <section id="third-party">
            <h2 className="mb-4 text-2xl font-bold text-white">
              5. Third-Party Services
            </h2>
            <div className="space-y-4">
              <p>
                We use trusted third-party services to provide and improve our
                Service:
              </p>

              <h3 className="text-lg font-semibold text-white">Google OAuth</h3>
              <p>
                For authentication. Google's privacy policy:{' '}
                <a
                  href="https://policies.google.com/privacy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  https://policies.google.com/privacy
                </a>
              </p>

              <h3 className="mt-4 text-lg font-semibold text-white">
                Checkout.com
              </h3>
              <p>
                For payment processing. Checkout.com's privacy policy:{' '}
                <a
                  href="https://www.checkout.com/legal/privacy-policy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  https://www.checkout.com/legal/privacy-policy
                </a>
              </p>

              <h3 className="mt-4 text-lg font-semibold text-white">
                Analytics Tools
              </h3>
              <p>
                We may use privacy-focused analytics tools to understand how users
                interact with the Service. We do not use Google Analytics or other
                invasive tracking tools. Any analytics data collected is
                anonymized and aggregated.
              </p>

              <p className="mt-4">
                These third parties have access to your information only to
                perform tasks on our behalf and are obligated not to disclose or
                use it for other purposes.
              </p>
            </div>
          </section>

          {/* Section 6 */}
          <section id="cookies">
            <h2 className="mb-4 text-2xl font-bold text-white">
              6. Cookies & Tracking
            </h2>
            <div className="space-y-4">
              <p>
                We use cookies and similar tracking technologies to provide and
                improve the Service:
              </p>

              <h3 className="text-lg font-semibold text-white">
                Essential Cookies
              </h3>
              <p>Required for authentication and core functionality:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Session cookies (authentication tokens)</li>
                <li>Security cookies (CSRF protection)</li>
                <li>Preference cookies (theme, language)</li>
              </ul>

              <h3 className="mt-6 text-lg font-semibold text-white">
                Optional Cookies
              </h3>
              <p>Used for analytics and service improvement (you can opt out):</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Usage analytics</li>
                <li>Performance monitoring</li>
                <li>Feature usage tracking</li>
              </ul>

              <h3 className="mt-6 text-lg font-semibold text-white">
                Managing Cookies
              </h3>
              <p>
                You can control cookies through your browser settings. Disabling
                essential cookies may impact your ability to use the Service.
              </p>
            </div>
          </section>

          {/* Section 7 */}
          <section id="your-rights">
            <h2 className="mb-4 text-2xl font-bold text-white">
              7. Your Rights (GDPR)
            </h2>
            <div className="space-y-4">
              <p>
                If you are in the European Economic Area (EEA), you have the
                following rights under GDPR:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>
                  <strong>Access:</strong> Request a copy of all personal data we
                  hold about you
                </li>
                <li>
                  <strong>Rectification:</strong> Request correction of inaccurate
                  or incomplete data
                </li>
                <li>
                  <strong>Deletion:</strong> Request deletion of your personal
                  data ("right to be forgotten")
                </li>
                <li>
                  <strong>Portability:</strong> Request a copy of your data in a
                  machine-readable format
                </li>
                <li>
                  <strong>Restriction:</strong> Request limitation on how we use
                  your data
                </li>
                <li>
                  <strong>Objection:</strong> Object to our processing of your
                  data
                </li>
                <li>
                  <strong>Withdraw Consent:</strong> Withdraw consent for data
                  processing at any time
                </li>
              </ul>
              <p className="mt-4">
                To exercise these rights, contact us at 
                perpetua@404mw.com.
                We will respond within 30 days.
              </p>
            </div>
          </section>

          {/* Section 8 */}
          <section id="children">
            <h2 className="mb-4 text-2xl font-bold text-white">
              8. Children's Privacy
            </h2>
            <div className="space-y-4">
              <p>
                The Service is not intended for children under 13 years of age. We
                do not knowingly collect personal information from children under
                13.
              </p>
              <p>
                If we discover that we have collected information from a child
                under 13, we will delete it immediately. If you believe we have
                collected information from a child, please contact us at
                pereptua@404mw.com.
              </p>
            </div>
          </section>

          {/* Section 9 */}
          <section id="open-source">
            <h2 className="mb-4 text-2xl font-bold text-white">
              9. Open Source Notice
            </h2>
            <div className="space-y-4">
              <p>
                Perpetua is an open-source project available on GitHub. The source
                code is publicly accessible, allowing anyone to review how we
                handle data and security.
              </p>
              <p>
                Repository:{' '}
                <a
                  href="https://github.com/404mw/TODO-GIAIC"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  404mw/Perpetua
                </a>
              </p>
              <p>
                While the code is open source, your personal data and User Content
                remain private and are not shared publicly.
              </p>
            </div>
          </section>

          {/* Section 10 */}
          <section id="data-sharing">
            <h2 className="mb-4 text-2xl font-bold text-white">
              10. Data Sharing
            </h2>
            <div className="space-y-4">
              <p>We do not sell your personal data to third parties.</p>
              <p>We may share your information only in the following cases:</p>
              <ul className="list-disc space-y-2 pl-6">
                <li>
                  <strong>With Your Consent:</strong> When you explicitly
                  authorize sharing
                </li>
                <li>
                  <strong>Service Providers:</strong> With trusted third parties
                  who help us provide the Service (Google, Checkout.com)
                </li>
                <li>
                  <strong>Legal Requirements:</strong> When required by law,
                  subpoena, or court order
                </li>
                <li>
                  <strong>Safety:</strong> To protect the safety, rights, or
                  property of our users or the public
                </li>
                <li>
                  <strong>Business Transfer:</strong> In connection with a merger,
                  acquisition, or sale of assets (with notice to you)
                </li>
              </ul>
            </div>
          </section>

          {/* Section 11 */}
          <section id="california">
            <h2 className="mb-4 text-2xl font-bold text-white">
              11. California Privacy Rights (CCPA)
            </h2>
            <div className="space-y-4">
              <p>
                If you are a California resident, you have additional rights under
                the California Consumer Privacy Act (CCPA):
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>
                  <strong>Right to Know:</strong> Request information about the
                  personal data we collect, use, and share
                </li>
                <li>
                  <strong>Right to Delete:</strong> Request deletion of your
                  personal data
                </li>
                <li>
                  <strong>Right to Opt-Out:</strong> Opt out of the sale of
                  personal data (we don't sell data)
                </li>
                <li>
                  <strong>Non-Discrimination:</strong> We will not discriminate
                  against you for exercising your CCPA rights
                </li>
              </ul>
              <p className="mt-4">
                To exercise these rights, contact us at perpetua@404mw.com
                or use our{' '}
                <Link href="/contact" className="text-blue-400 hover:underline">
                  contact form
                </Link>
                .
              </p>
            </div>
          </section>

          {/* Section 12 */}
          <section id="changes">
            <h2 className="mb-4 text-2xl font-bold text-white">
              12. Changes to This Policy
            </h2>
            <div className="space-y-4">
              <p>
                We may update this Privacy Policy from time to time. When we make
                material changes, we will notify you by:
              </p>
              <ul className="list-disc space-y-2 pl-6">
                <li>Posting a notice on the Service</li>
                <li>Sending an email to the address associated with your account</li>
                <li>Updating the "Last Updated" date at the top of this page</li>
              </ul>
              <p>
                We encourage you to review this Privacy Policy periodically. Your
                continued use of the Service after changes are posted constitutes
                your acceptance of the updated policy.
              </p>
            </div>
          </section>

          {/* Section 13 */}
          <section id="contact">
            <h2 className="mb-4 text-2xl font-bold text-white">13. Contact Us</h2>
            <div className="space-y-4">
              <p>
                If you have any questions about this Privacy Policy or how we
                handle your data, please contact us:
              </p>
              <div className="rounded-lg border border-white/10 bg-white/5 p-4">
                <p className="font-medium text-white">Perpetua Flow</p>
                <p>Email: pereptua@404mw.com</p>
                <p>Support: pereptua@404mw.com</p>
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
              By using Perpetua, you acknowledge that you have read and
              understood this Privacy Policy and consent to our data practices as
              described.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
