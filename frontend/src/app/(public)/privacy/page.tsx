/**
 * Privacy Policy Page
 *
 * Legal document outlining how Perpetua Flow collects, uses, and protects user data.
 * Last Updated: February 8, 2026
 */

'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

export default function PrivacyPage() {
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
            Privacy Policy
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-400">
            Your privacy matters. Learn how we collect, use, and protect your personal information.
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
            <h2 className="text-2xl font-bold text-white mb-4">1. Introduction</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Welcome to Perpetua Flow's Privacy Policy. This document explains how we collect, use, store, and protect your personal information when you use our task management service.
              </p>
              <p>
                We are committed to protecting your privacy and complying with applicable data protection laws, including the General Data Protection Regulation (GDPR) and other international privacy standards.
              </p>
              <p>
                By using Perpetua Flow, you consent to the data practices described in this policy. If you do not agree with this policy, please do not use our Service.
              </p>
            </div>
          </motion.div>

          {/* Information We Collect */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.15 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">2. Information We Collect</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>2.1 Information from Google OAuth:</strong>
              </p>
              <p>
                When you sign in using Google OAuth, we collect:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Your full name</li>
                <li>Your email address</li>
                <li>Your Google profile picture (if available)</li>
                <li>A unique Google user identifier</li>
              </ul>
              <p>
                We use this information solely for account creation, authentication, and personalization purposes.
              </p>

              <p>
                <strong>2.2 User-Generated Content:</strong>
              </p>
              <p>
                When you use Perpetua Flow, we collect and store:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Tasks, subtasks, and task descriptions you create</li>
                <li>Notes and note content</li>
                <li>Tags and categories you assign</li>
                <li>Completion status and completion dates</li>
                <li>Streak data and consistency tracking</li>
                <li>Focus mode session data (duration, completion)</li>
                <li>Achievement progress and unlocked achievements</li>
                <li>Reminder preferences and notification settings</li>
              </ul>

              <p>
                <strong>2.3 Usage Analytics:</strong>
              </p>
              <p>
                We collect anonymous usage data to improve the Service:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Pages viewed and features used</li>
                <li>Time spent in the application</li>
                <li>Browser type and version</li>
                <li>Device type (desktop, mobile, tablet)</li>
                <li>Screen resolution</li>
                <li>Error logs and crash reports</li>
              </ul>
              <p>
                This data is aggregated and anonymized. We do not track your location or use tracking cookies for advertising purposes.
              </p>

              <p>
                <strong>2.4 Local Storage Data:</strong>
              </p>
              <p>
                We use browser local storage and session storage to store:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>UI preferences (sidebar state, theme preferences)</li>
                <li>Authentication tokens (for session management)</li>
                <li>Temporary draft content (auto-saved as you type)</li>
              </ul>
              <p>
                This data remains on your device and is not transmitted to our servers except where necessary for Service functionality.
              </p>
            </div>
          </motion.div>

          {/* How We Use Your Information */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.2 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">3. How We Use Your Information</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                We use the information we collect for the following purposes:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Provide the Service:</strong> Store your tasks, notes, and productivity data</li>
                <li><strong>Authentication:</strong> Verify your identity and manage your account</li>
                <li><strong>Personalization:</strong> Display your name and profile picture in the UI</li>
                <li><strong>AI Features:</strong> Process your task descriptions to generate subtask suggestions (Pro tier only)</li>
                <li><strong>Notifications:</strong> Send browser notifications and reminder alerts based on your preferences</li>
                <li><strong>Communication:</strong> Send service updates, feature announcements, and support responses</li>
                <li><strong>Analytics:</strong> Understand how users interact with the Service to improve features and fix bugs</li>
                <li><strong>Security:</strong> Detect and prevent fraud, abuse, and unauthorized access</li>
                <li><strong>Legal Compliance:</strong> Comply with applicable laws, regulations, and legal processes</li>
              </ul>
              <p>
                We do NOT use your data for:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Selling or renting your personal information to third parties</li>
                <li>Displaying targeted advertising based on your activity</li>
                <li>Sharing your task content with other users (unless you explicitly share)</li>
              </ul>
            </div>
          </motion.div>

          {/* Data Storage & Security */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.25 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">4. Data Storage and Security</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Data Storage:</strong> Your data is stored on secure cloud servers. We use industry-standard database encryption and access controls to protect your information.
              </p>
              <p>
                <strong>Encryption:</strong> All data transmitted between your browser and our servers is encrypted using HTTPS/TLS. Sensitive data at rest is encrypted using AES-256 encryption.
              </p>
              <p>
                <strong>Access Controls:</strong> Access to user data is restricted to authorized personnel who need it to operate, develop, or improve the Service. All access is logged and monitored.
              </p>
              <p>
                <strong>Security Measures:</strong> We implement security best practices including:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Regular security audits and vulnerability assessments</li>
                <li>Firewalls and intrusion detection systems</li>
                <li>Secure authentication using OAuth 2.0</li>
                <li>Automated backups with encryption</li>
                <li>Incident response procedures</li>
              </ul>
              <p>
                <strong>Data Breaches:</strong> In the unlikely event of a data breach, we will notify affected users within 72 hours in accordance with GDPR requirements.
              </p>
              <p className="text-sm text-gray-500">
                Note: While we use industry-standard security measures, no system is 100% secure. You are responsible for maintaining the security of your Google account credentials.
              </p>
            </div>
          </motion.div>

          {/* Third-Party Services */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.3 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">5. Third-Party Services</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Perpetua Flow integrates with the following third-party services:
              </p>
              <p>
                <strong>5.1 Google OAuth (Google LLC):</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Purpose: User authentication and account creation</li>
                <li>Data Shared: Name, email, profile picture</li>
                <li>Privacy Policy: <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">Google Privacy Policy</a></li>
              </ul>

              <p>
                <strong>5.2 AI Service Providers (OpenAI):</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Purpose: AI-powered subtask generation (Pro tier only)</li>
                <li>Data Shared: Task titles and descriptions you choose to process with AI</li>
                <li>Data Retention: AI providers do not retain your prompts after processing (zero data retention policy)</li>
              </ul>

              <p>
                <strong>5.3 Payment Processor (if applicable):</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Purpose: Process subscription payments</li>
                <li>Data Shared: Billing information, payment method details</li>
                <li>Note: We do not store full credit card numbers on our servers</li>
              </ul>

              <p>
                We carefully vet all third-party services to ensure they meet our privacy and security standards. These services are bound by their own privacy policies and data protection agreements.
              </p>
            </div>
          </motion.div>

          {/* GDPR Rights */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.35 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">6. Your Rights Under GDPR</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                If you are located in the European Economic Area (EEA), United Kingdom, or other jurisdiction with similar privacy laws, you have the following rights:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong>Right to Access:</strong> Request a copy of all personal data we hold about you
                </li>
                <li>
                  <strong>Right to Rectification:</strong> Request correction of inaccurate or incomplete data
                </li>
                <li>
                  <strong>Right to Erasure ("Right to be Forgotten"):</strong> Request deletion of your personal data
                </li>
                <li>
                  <strong>Right to Data Portability:</strong> Receive your data in a structured, machine-readable format (JSON)
                </li>
                <li>
                  <strong>Right to Restrict Processing:</strong> Limit how we process your data
                </li>
                <li>
                  <strong>Right to Object:</strong> Object to processing of your data for certain purposes
                </li>
                <li>
                  <strong>Right to Withdraw Consent:</strong> Withdraw your consent at any time
                </li>
                <li>
                  <strong>Right to Lodge a Complaint:</strong> File a complaint with your local data protection authority
                </li>
              </ul>
              <p>
                <strong>How to Exercise Your Rights:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Access your data: Available in your account settings under "Data Export"</li>
                <li>Delete your account: Settings → Account → "Delete Account"</li>
                <li>Contact us: Email <a href="mailto:privacy@perpetuaflow.com" className="text-blue-400 hover:text-blue-300 underline">privacy@perpetuaflow.com</a> for other requests</li>
              </ul>
              <p>
                We will respond to your request within 30 days. If we need additional time, we will notify you of the reason and extension period.
              </p>
            </div>
          </motion.div>

          {/* Cookies & Storage */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.4 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">7. Cookies and Local Storage</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Perpetua Flow uses cookies and browser storage technologies to provide functionality and improve your experience.
              </p>
              <p>
                <strong>Essential Cookies:</strong> Required for authentication and basic functionality
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Authentication tokens (to keep you logged in)</li>
                <li>Session identifiers</li>
                <li>Security tokens (CSRF protection)</li>
              </ul>
              <p>
                <strong>Functional Storage:</strong> Enhance your experience
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>UI preferences (sidebar state, theme)</li>
                <li>Draft content (auto-save)</li>
                <li>Recently viewed items</li>
              </ul>
              <p>
                <strong>Analytics Cookies:</strong> Help us understand usage patterns (anonymized)
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Page view tracking</li>
                <li>Feature usage statistics</li>
                <li>Error reporting</li>
              </ul>
              <p>
                <strong>We DO NOT use:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Third-party advertising cookies</li>
                <li>Cross-site tracking cookies</li>
                <li>Social media tracking pixels</li>
              </ul>
              <p>
                You can clear cookies and local storage through your browser settings. Note that this may log you out and reset your preferences.
              </p>
            </div>
          </motion.div>

          {/* Data Retention */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.45 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">8. Data Retention</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                <strong>Active Accounts:</strong> We retain your data for as long as your account is active or as needed to provide you with the Service.
              </p>
              <p>
                <strong>Account Deletion:</strong> When you delete your account:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Your personal data and content are permanently deleted within 30 days</li>
                <li>Backups containing your data are purged within 90 days</li>
                <li>Some metadata may be retained in anonymized form for analytics</li>
              </ul>
              <p>
                <strong>Legal Requirements:</strong> We may retain certain data longer if required by law, for legal proceedings, or to enforce our Terms of Service.
              </p>
              <p>
                <strong>Inactive Accounts:</strong> Accounts inactive for more than 3 years may be archived or deleted with advance notice.
              </p>
            </div>
          </motion.div>

          {/* Children's Privacy */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.5 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">9. Children's Privacy (COPPA Compliance)</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Perpetua Flow is not intended for children under the age of 13. We do not knowingly collect personal information from children under 13.
              </p>
              <p>
                If you are a parent or guardian and believe your child has provided us with personal information, please contact us immediately at <a href="mailto:privacy@perpetuaflow.com" className="text-blue-400 hover:text-blue-300 underline">privacy@perpetuaflow.com</a>. We will delete such information from our systems promptly.
              </p>
              <p>
                Users between 13 and 18 years old should obtain parental consent before using the Service.
              </p>
            </div>
          </motion.div>

          {/* International Data Transfers */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.55 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">10. International Data Transfers</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                Your data may be transferred to and processed in countries other than your country of residence. These countries may have data protection laws that differ from those in your jurisdiction.
              </p>
              <p>
                When we transfer data internationally, we ensure appropriate safeguards are in place, including:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Standard Contractual Clauses (SCCs) approved by the European Commission</li>
                <li>Data processing agreements with third-party services</li>
                <li>Compliance with relevant data protection frameworks</li>
              </ul>
              <p>
                By using Perpetua Flow, you consent to the transfer of your data to countries outside your jurisdiction as described in this policy.
              </p>
            </div>
          </motion.div>

          {/* Changes to Privacy Policy */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.6 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">11. Changes to This Privacy Policy</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                We may update this Privacy Policy from time to time to reflect changes in our practices, technology, legal requirements, or other factors.
              </p>
              <p>
                When we make material changes, we will:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Update the "Last Updated" date at the top of this policy</li>
                <li>Notify you via email (if you have provided your email)</li>
                <li>Display a prominent notice in the application</li>
                <li>Request your consent if required by law</li>
              </ul>
              <p>
                We encourage you to review this Privacy Policy periodically. Your continued use of the Service after changes are posted constitutes your acceptance of the updated policy.
              </p>
            </div>
          </motion.div>

          {/* Contact Information */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.65 }}
            className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
          >
            <h2 className="text-2xl font-bold text-white mb-4">12. Contact Us</h2>
            <div className="space-y-4 text-gray-400">
              <p>
                If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
              </p>
              <ul className="space-y-2 ml-4">
                <li>
                  <strong>Privacy Inquiries:</strong>{' '}
                  <a href="mailto:privacy@perpetuaflow.com" className="text-blue-400 hover:text-blue-300 underline">
                    privacy@perpetuaflow.com
                  </a>
                </li>
                <li>
                  <strong>Data Protection Officer:</strong>{' '}
                  <a href="mailto:dpo@perpetuaflow.com" className="text-blue-400 hover:text-blue-300 underline">
                    dpo@perpetuaflow.com
                  </a>
                </li>
                <li>
                  <strong>General Inquiries:</strong>{' '}
                  <Link href="/contact" className="text-blue-400 hover:text-blue-300 underline">
                    perpetuaflow.com/contact
                  </Link>
                </li>
              </ul>
              <p>
                We will respond to all privacy-related requests within 30 days.
              </p>
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
          transition={{ delay: 0.7 }}
          className="mx-auto max-w-4xl rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-12 text-center backdrop-blur-sm"
        >
          <h2 className="text-3xl font-bold text-white">
            Your privacy is our priority
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-gray-300">
            We're committed to protecting your data and being transparent about our practices.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link
              href="/dashboard"
              className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
            >
              Get Started Free
            </Link>
            <Link
              href="/terms"
              className="rounded-lg border border-white/20 bg-white/5 px-6 py-3 font-medium text-white transition-colors hover:bg-white/10"
            >
              Terms of Service
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  )
}
