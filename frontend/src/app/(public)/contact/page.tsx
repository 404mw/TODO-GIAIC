/**
 * Contact Page (T155)
 * Phase 13 - Public Pages
 *
 * Contact form with:
 * - Name, email, message fields
 * - Validation feedback
 * - Dark aesthetic matching other public pages
 *
 * FR-066: Contact page with form
 */

'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

interface FormData {
  name: string
  email: string
  subject: string
  message: string
}

interface FormErrors {
  name?: string
  email?: string
  subject?: string
  message?: string
}

export default function ContactPage() {
  const shouldReduceMotion = useReducedMotion()
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    subject: '',
    message: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }

    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required'
    }

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required'
    } else if (formData.message.length < 10) {
      newErrors.message = 'Message must be at least 10 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))

    setIsSubmitting(false)
    setIsSubmitted(true)
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const fadeIn = shouldReduceMotion
    ? {}
    : {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.4 },
      }

  if (isSubmitted) {
    return (
      <div className="min-h-[80vh] px-4 py-24">
        <motion.div
          {...fadeIn}
          className="mx-auto max-w-lg text-center"
        >
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
            <svg
              className="h-8 w-8 text-green-400"
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
          <h1 className="text-3xl font-bold text-white">Message Sent!</h1>
          <p className="mt-4 text-gray-400">
            Thank you for reaching out. We'll get back to you within 24-48 hours.
          </p>
          <button
            onClick={() => {
              setIsSubmitted(false)
              setFormData({ name: '', email: '', subject: '', message: '' })
            }}
            className="mt-8 rounded-lg bg-white/10 px-6 py-2 text-sm font-medium text-white transition-colors hover:bg-white/20"
          >
            Send Another Message
          </button>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen px-4 py-24">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <motion.div {...fadeIn} className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white">Get in Touch</h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-400">
            Have a question or feedback? We'd love to hear from you. Fill out
            the form below and we'll respond as soon as possible.
          </p>
        </motion.div>

        <div className="grid gap-12 lg:grid-cols-2">
          {/* Contact Form */}
          <motion.div
            {...fadeIn}
            transition={{ ...fadeIn.transition, delay: 0.1 }}
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name Field */}
              <div>
                <label
                  htmlFor="name"
                  className="mb-2 block text-sm font-medium text-gray-300"
                >
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full rounded-lg border bg-white/5 px-4 py-3 text-white placeholder-gray-500 backdrop-blur-sm transition-colors focus:outline-none focus:ring-2 ${
                    errors.name
                      ? 'border-red-500 focus:ring-red-500'
                      : 'border-white/10 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                  placeholder="Your name"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-400">{errors.name}</p>
                )}
              </div>

              {/* Email Field */}
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-medium text-gray-300"
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full rounded-lg border bg-white/5 px-4 py-3 text-white placeholder-gray-500 backdrop-blur-sm transition-colors focus:outline-none focus:ring-2 ${
                    errors.email
                      ? 'border-red-500 focus:ring-red-500'
                      : 'border-white/10 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                  placeholder="you@example.com"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-400">{errors.email}</p>
                )}
              </div>

              {/* Subject Field */}
              <div>
                <label
                  htmlFor="subject"
                  className="mb-2 block text-sm font-medium text-gray-300"
                >
                  Subject
                </label>
                <select
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  className={`w-full rounded-lg border bg-white/5 px-4 py-3 text-white backdrop-blur-sm transition-colors focus:outline-none focus:ring-2 ${
                    errors.subject
                      ? 'border-red-500 focus:ring-red-500'
                      : 'border-white/10 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                >
                  <option value="" className="bg-gray-900">
                    Select a topic
                  </option>
                  <option value="general" className="bg-gray-900">
                    General Inquiry
                  </option>
                  <option value="support" className="bg-gray-900">
                    Technical Support
                  </option>
                  <option value="feedback" className="bg-gray-900">
                    Feedback
                  </option>
                  <option value="partnership" className="bg-gray-900">
                    Partnership
                  </option>
                  <option value="other" className="bg-gray-900">
                    Other
                  </option>
                </select>
                {errors.subject && (
                  <p className="mt-1 text-sm text-red-400">{errors.subject}</p>
                )}
              </div>

              {/* Message Field */}
              <div>
                <label
                  htmlFor="message"
                  className="mb-2 block text-sm font-medium text-gray-300"
                >
                  Message
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows={5}
                  className={`w-full resize-none rounded-lg border bg-white/5 px-4 py-3 text-white placeholder-gray-500 backdrop-blur-sm transition-colors focus:outline-none focus:ring-2 ${
                    errors.message
                      ? 'border-red-500 focus:ring-red-500'
                      : 'border-white/10 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                  placeholder="Tell us what's on your mind..."
                />
                {errors.message && (
                  <p className="mt-1 text-sm text-red-400">{errors.message}</p>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="h-5 w-5 animate-spin"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Sending...
                  </span>
                ) : (
                  'Send Message'
                )}
              </button>
            </form>
          </motion.div>

          {/* Contact Info */}
          <motion.div
            {...fadeIn}
            transition={{ ...fadeIn.transition, delay: 0.2 }}
            className="space-y-8"
          >
            {/* Email */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/20">
                  <svg
                    className="h-5 w-5 text-blue-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-white">Email</h3>
                  <p className="mt-1 text-gray-400">support@perpetua.app</p>
                  <p className="mt-1 text-sm text-gray-500">
                    We respond within 24-48 hours
                  </p>
                </div>
              </div>
            </div>

            {/* Social */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/20">
                  <svg
                    className="h-5 w-5 text-purple-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-white">Social Media</h3>
                  <p className="mt-1 text-gray-400">
                    Follow us for updates and tips
                  </p>
                  <div className="mt-3 flex gap-3">
                    <a
                      href="https://twitter.com/perpetua"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 transition-colors hover:text-white"
                    >
                      Twitter
                    </a>
                    <a
                      href="https://github.com/perpetua"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 transition-colors hover:text-white"
                    >
                      GitHub
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* FAQ Link */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/20">
                  <svg
                    className="h-5 w-5 text-green-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-white">FAQ</h3>
                  <p className="mt-1 text-gray-400">
                    Check our pricing page for frequently asked questions about
                    plans and features.
                  </p>
                  <a
                    href="/pricing"
                    className="mt-3 inline-block text-sm text-blue-400 hover:text-blue-300"
                  >
                    View FAQ →
                  </a>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
