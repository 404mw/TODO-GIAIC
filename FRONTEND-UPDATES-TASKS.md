# Frontend Update Tasks

**Project**: Perpetua Flow (02-TODO)
**Branch**: 002-perpetua-frontend
**Document Created**: 2026-02-09

---

## Overview

This document outlines all frontend updates, fixes, and new features to be implemented. Tasks are organized into 6 logical phases for easier tracking and incremental testing.

### Summary by Phase
- **Phase 1**: Public Pages Updates (Home, Pricing, About, Legal)
- **Phase 2**: Dashboard Fixes (Sidebar, Settings, Notes, Profile)
- **Phase 3**: Credits System
- **Phase 4**: Payment Integration (Checkout.com)
- **Phase 5**: Google OAuth Integration
- **Phase 6**: Achievements System

---

## Phase 1: Public Pages Updates

### Homepage ([page.tsx](frontend/src/app/page.tsx))

**1.1 Emphasize Free Tier Generosity**
- [X] Add prominent CTA section after hero highlighting free features
  - [X] Create new section component with heading "Start Free - No Credit Card Required"
  - [X] List key free features: 50 tasks, streak tracking, notes, focus mode, notifications
  - [X] Add visual distinction (gradient background, icons)
  - [X] Add CTA button linking to `/dashboard`
- [X] Update hero section subtitle to mention "completely free to start"
- [X] Update final CTA section to emphasize no cost to get started

**1.2 Add Open Source Badge**
- [X] Add "Open Source" badge/mention in footer or about section
- [X] Include GitHub repository link

---

### Pricing Page ([pricing/page.tsx](frontend/src/app/(public)/pricing/page.tsx))

**1.3 Update Pricing with Real Data**
- [X] Research and document actual pricing tiers and features
- [X] Update `PLANS` constant with real pricing data:
  - [X] Free tier: Verify 50 task limit, list exact features
  - [X] Pro tier: Finalize price ($9/mo or updated), list exact features
- [X] Ensure feature lists match backend subscription capabilities

**1.4 Add Plan Comparison Section**
- [X] Create comparison table component showing Free vs Pro side-by-side
- [X] Add checkmarks for included features, X or dash for excluded
- [X] Include features: Task limits, AI subtasks, Recurring tasks, Analytics, Themes, Support, Cloud sync, Export
- [X] Make table responsive (collapse to accordion on mobile)

**1.5 Expand FAQ Section**
- [X] Add 3-5 more FAQ entries covering:
  - [X] "How do I upgrade from Free to Pro?"
  - [X] "Can I cancel anytime?"
  - [X] "Do you offer refunds?"
  - [X] "What payment methods do you accept?"
  - [X] "Is my data secure?"
- [X] Update existing FAQ answers for clarity

---

### About Page ([about/page.tsx](frontend/src/app/(public)/about/page.tsx))

**1.6 Add Free Tier Value Proposition**
- [X] Add new value card in VALUES section:
  - [X] Title: "Free Forever Core"
  - [X] Message: "We believe productivity tools should be accessible. Perpetua's core features are completely free—no trials, no credit card required, no hidden fees."
  - [X] Icon: Gift or heart icon (theme: generosity)
- [X] Update mission section to mention commitment to free tier

**1.7 Remove Tech Stack Section**
- [X] Remove "Built with Modern Tech" section (lines 246-269)
- [X] Remove tech badges display

---

### New Legal Pages

**1.8 Create Terms of Service Page**
- [X] Create file: `frontend/src/app/(public)/terms/page.tsx`
- [X] Create layout: `frontend/src/app/(public)/terms/layout.tsx`
- [X] Create metadata: `frontend/src/app/(public)/terms/metadata.ts`
- [X] Write comprehensive ToS covering:
  - [X] **Acceptance of Terms**: User agreement to terms
  - [X] **Service Description**: What Perpetua provides
  - [X] **User Accounts**: Registration, security, termination
  - [X] **Subscription & Billing**: Free/Pro tiers, payment terms, refunds
  - [X] **User Content**: Ownership, license granted to us, prohibited content
  - [X] **Acceptable Use**: Prohibited activities (spam, hacking, abuse)
  - [X] **Intellectual Property**: Our ownership of app code/design
  - [X] **Disclaimers**: As-is service, no warranties
  - [X] **Limitation of Liability**: Damage limitations
  - [X] **Termination**: Our right to suspend/terminate accounts
  - [X] **Changes to Terms**: How we'll notify users
  - [X] **Governing Law**: Jurisdiction and dispute resolution
  - [X] **Contact Information**: Support email
- [X] Use dark theme matching other public pages
- [X] Add last updated date at top
- [X] Add table of contents for easy navigation

**1.9 Create Privacy Policy Page**
- [X] Create file: `frontend/src/app/(public)/privacy/page.tsx`
- [X] Create layout: `frontend/src/app/(public)/privacy/layout.tsx`
- [X] Create metadata: `frontend/src/app/(public)/privacy/metadata.ts`
- [X] Write comprehensive Privacy Policy covering:
  - [X] **Information We Collect**: Account info, usage data, cookies
  - [X] **How We Use Information**: Service provision, analytics, communication
  - [X] **Data Storage & Security**: Encryption, storage location, retention
  - [X] **Third-Party Services**: Google OAuth, Checkout.com, analytics
  - [X] **Cookies & Tracking**: What we track, how to opt out
  - [X] **Your Rights (GDPR)**: Access, deletion, export, portability
  - [X] **Children's Privacy**: Age requirements (13+)
  - [X] **Open Source Notice**: Mention project is open source on GitHub
  - [X] **Data Sharing**: We don't sell data, when we share (legal requirements)
  - [X] **California Privacy Rights (CCPA)**: If applicable
  - [X] **Changes to Policy**: Notification process
  - [X] **Contact Us**: Privacy email/support
- [X] Use dark theme matching other public pages
- [X] Add last updated date at top
- [X] Add table of contents for easy navigation

**1.10 Update Footer with Legal Links**
- [X] Update [Footer.tsx](frontend/src/components/public/Footer.tsx)
- [X] Verify LEGAL_LINKS array includes:
  - [X] Privacy Policy → `/privacy`
  - [X] Terms of Service → `/terms`
- [X] Add "Open Source" link to GitHub repository in footer
- [X] Update copyright year dynamically

---

## Phase 2: Dashboard Fixes

### Sidebar ([Sidebar.tsx](frontend/src/components/layout/Sidebar.tsx))

**2.1 Fix Sidebar Collapse Functionality**
- [ ] Test current sidebar toggle on desktop
- [ ] If broken, debug `useSidebarStore` toggle function
- [ ] Verify flap button (line 72-91) calls toggle correctly
- [ ] Test collapsed/expanded states with different screen sizes

**2.2 Fix Mobile Sidebar Behavior**
- [ ] Ensure sidebar starts collapsed on mobile (< 1024px)
- [ ] Fix overlay positioning: sidebar should slide over content, not push it
- [ ] Verify z-index: sidebar (z-40) should be below overlay (z-50)
- [ ] Test hamburger button in [Header.tsx](frontend/src/components/layout/Header.tsx)
- [ ] Ensure clicking overlay closes sidebar on mobile
- [ ] Add swipe-to-close gesture (optional enhancement)

**2.3 Add Hamburger Menu (if missing)**
- [ ] Check [Header.tsx](frontend/src/components/layout/Header.tsx) lines 64-98
- [ ] Verify hamburger icon displays on screens < 1024px
- [ ] Ensure it toggles sidebar open/closed
- [ ] Test icon changes between menu and X when open

---

### Settings Pages

**2.4 Fix Hidden Tasks Back Button**
- [ ] Open [hidden-tasks/page.tsx](frontend/src/app/dashboard/settings/hidden-tasks/page.tsx) line 76
- [ ] Change href from `/settings` to `/dashboard/settings`
- [ ] Test navigation: Hidden Tasks → Settings (should work)
- [ ] Test breadcrumb trail if present

**2.5 Disable Preferences Section**
- [ ] Open [settings/page.tsx](frontend/src/app/dashboard/settings/page.tsx)
- [ ] Find "Preferences" section (line 38-58)
- [ ] Add `disabled` or `opacity-50 cursor-not-allowed` styling
- [ ] Add tooltip: "Coming soon"
- [ ] Prevent navigation when clicked (add `onClick={(e) => e.preventDefault()}`)

**2.6 Fix Onboarding Replay**
- [ ] Check "Replay Onboarding" link in settings (line 60-79)
- [ ] Change href from `/dashboard/settings/onboarding` to a valid route
- [ ] Option A: Create `/dashboard/settings/onboarding/page.tsx` that auto-starts tour
- [ ] Option B: Add onClick handler to trigger onboarding:
  ```tsx
  import { resetOnboarding } from '@/components/onboarding/OnboardingTour'
  import { useOnboardingTour } from '@/components/onboarding/OnboardingTour'

  const { startTour } = useOnboardingTour()
  onClick={() => {
    resetOnboarding()
    startTour()
  }}
  ```
- [ ] Test onboarding replay from settings

---

### Notes Page ([notes/page.tsx](frontend/src/app/dashboard/notes/page.tsx))

**2.7 Move Archive to Settings**
- [ ] Remove "Show Archived" button from main Notes page header (line 55-60)
- [ ] Create new settings page: `frontend/src/app/dashboard/settings/archived-notes/page.tsx`
- [ ] Add "Archived Notes" to settings sections in [settings/page.tsx](frontend/src/app/dashboard/settings/page.tsx):
  ```tsx
  {
    title: 'Archived Notes',
    message: 'View and manage notes you have archived',
    href: '/dashboard/settings/archived-notes',
    icon: <ArchiveIcon />
  }
  ```
- [ ] Copy archived notes view logic to new settings page
- [ ] Add back button linking to `/dashboard/settings`
- [ ] Test archive/unarchive functionality from settings

---

### Header ([Header.tsx](frontend/src/components/layout/Header.tsx))

**2.8 Fix "+ New" Dropdown for Notes**
- [ ] Open [Header.tsx](frontend/src/components/layout/Header.tsx) line 53-57
- [ ] Replace `console.log('New note clicked')` with actual note creation:
  ```tsx
  import { useRouter } from 'next/navigation'
  const router = useRouter()

  const handleNewNote = () => {
    setShowNewDropdown(false)
    router.push('/dashboard/notes?create=true')
  }
  ```
- [ ] Update [notes/page.tsx](frontend/src/app/dashboard/notes/page.tsx) to handle `?create=true` query:
  ```tsx
  const searchParams = useSearchParams()
  useEffect(() => {
    if (searchParams.get('create') === 'true') {
      setIsCreating(true)
    }
  }, [searchParams])
  ```
- [ ] Test: Click "+ New" → "New Note" should open note editor

**2.9 Make Credits Button Functional**
- [ ] Update Credits button (line 118-137) to navigate to credits page:
  ```tsx
  <Link href="/dashboard/credits">
    <button className="flex items-center gap-1.5 ...">
      {/* existing icon and text */}
    </button>
  </Link>
  ```
- [ ] Note: Credits page will be created in Phase 3

---

### Profile Popover ([ProfilePopover.tsx](frontend/src/components/layout/ProfilePopover.tsx))

**2.10 Update User Display**
- [ ] Remove email display (line 54-56, 74-76)
- [ ] Add subscription plan display:
  ```tsx
  import { useSubscription } from '@/lib/hooks/useSubscription'

  const { data: subscription } = useSubscription()
  const plan = subscription?.data?.plan || 'free'

  <span className="text-xs text-gray-500 dark:text-gray-400">
    {plan === 'pro' ? '✨ Pro' : 'Free'}
  </span>
  ```
- [ ] Style Pro badge with gradient or special color

**2.11 Add Credits Button**
- [ ] Add "Credits" menu item after Settings (line 127):
  ```tsx
  <Link
    href="/dashboard/credits"
    className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors"
  >
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
    Credits
  </Link>
  ```

**2.12 Make View Profile Functional**
- [ ] Create profile page: `frontend/src/app/dashboard/profile/page.tsx`
- [ ] Include user info form: name, email (read-only), avatar upload
- [ ] Show subscription plan and status
- [ ] Add "Upgrade to Pro" CTA if on free plan
- [ ] Link from ProfilePopover already points to `/dashboard/profile` (line 84)

**2.13 Make Help & Support Functional**
- [ ] Update Help & Support link (line 129-147) to navigate to contact:
  ```tsx
  href="/contact"
  ```
- [ ] Alternatively, open contact page in new tab with external link icon

---

## Phase 3: Credits System

**3.1 Create Credits Schema**
- [ ] Create `frontend/src/lib/schemas/credit-detail.schema.ts`:
  ```tsx
  import { z } from 'zod'

  export const CreditSourceSchema = z.enum(['signup', 'subscription', 'purchase', 'bonus', 'refund'])

  export const CreditTransactionSchema = z.object({
    id: z.string(),
    user_id: z.string(),
    amount: z.number(),
    source: CreditSourceSchema,
    description: z.string(),
    created_at: z.string().datetime(),
  })

  export const CreditBalanceSchema = z.object({
    total_credits: z.number(),
    subscription_credits: z.number(),
    purchased_credits: z.number(),
    bonus_credits: z.number(),
  })

  export type CreditTransaction = z.infer<typeof CreditTransactionSchema>
  export type CreditBalance = z.infer<typeof CreditBalanceSchema>
  ```

**3.2 Create Credits API Hook**
- [ ] Update `frontend/src/lib/hooks/useCredits.ts`:
  ```tsx
  import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
  import { apiClient } from '@/lib/api/client'
  import type { CreditBalance, CreditTransaction } from '@/lib/schemas/credit-detail.schema'

  export function useCreditBalance() {
    return useQuery({
      queryKey: ['credits', 'balance'],
      queryFn: () => apiClient.get<{ data: CreditBalance }>('/credits/balance'),
    })
  }

  export function useCreditTransactions() {
    return useQuery({
      queryKey: ['credits', 'transactions'],
      queryFn: () => apiClient.get<{ data: CreditTransaction[] }>('/credits/transactions'),
    })
  }

  export function usePurchaseCredits() {
    const queryClient = useQueryClient()
    return useMutation({
      mutationFn: (amount: number) =>
        apiClient.post('/credits/purchase', { amount }),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['credits'] })
      },
    })
  }
  ```

**3.3 Create Credits Page**
- [ ] Create `frontend/src/app/dashboard/credits/page.tsx`
- [ ] Import hooks: `useCreditBalance`, `useCreditTransactions`
- [ ] Display credits overview card:
  - [ ] Total credits (large number)
  - [ ] Breakdown: Subscription, Purchased, Bonus (smaller text)
  - [ ] Visual progress bar or gauge
- [ ] Display transaction history table:
  - [ ] Columns: Date, Description, Source, Amount
  - [ ] Sort by date (newest first)
  - [ ] Pagination if > 20 transactions
  - [ ] Color code: green for additions, red for deductions
- [ ] Add "Purchase Credits" section:
  - [ ] Credit packages: 10 credits ($1), 50 credits ($4), 100 credits ($7)
  - [ ] Each package as a card with price and credit amount
  - [ ] "Buy Now" button on each (opens checkout flow)
- [ ] Show loading skeleton while fetching
- [ ] Handle error states

**3.4 Update Credits Button in Header**
- [ ] Verify link to `/dashboard/credits` works from Header
- [ ] Show current credit count in button (fetch from API):
  ```tsx
  const { data: balance } = useCreditBalance()
  <span>{balance?.data?.total_credits || 0}</span>
  ```
- [ ] Add loading state while fetching

---

## Phase 4: Payment Integration (Checkout.com)

**4.1 Research Backend Checkout.com Implementation**
- [ ] Locate backend payment routes (likely `/api/v1/payments/*`)
- [ ] Identify endpoints:
  - [ ] Create payment session
  - [ ] Handle payment callback/webhook
  - [ ] Purchase credits endpoint
  - [ ] Subscribe to Pro endpoint
- [ ] Document required request/response formats
- [ ] Check for environment variables needed (API keys, webhook URLs)

**4.2 Create Payment Service**
- [ ] Create `frontend/src/lib/services/payment.service.ts`:
  ```tsx
  import { apiClient } from '@/lib/api/client'

  export interface CreatePaymentSessionRequest {
    amount: number
    currency: string
    type: 'credit_purchase' | 'subscription'
    metadata?: Record<string, any>
  }

  export interface PaymentSession {
    session_id: string
    checkout_url: string
  }

  export const paymentService = {
    async createSession(request: CreatePaymentSessionRequest): Promise<PaymentSession> {
      const response = await apiClient.post<{ data: PaymentSession }>(
        '/payments/create-session',
        request
      )
      return response.data
    },

    async purchaseCredits(amount: number): Promise<PaymentSession> {
      return this.createSession({
        amount,
        currency: 'USD',
        type: 'credit_purchase',
        metadata: { credits: amount * 10 }
      })
    },

    async subscribeToPro(): Promise<PaymentSession> {
      return this.createSession({
        amount: 900, // $9.00 in cents
        currency: 'USD',
        type: 'subscription',
        metadata: { plan: 'pro' }
      })
    }
  }
  ```

**4.3 Implement Credit Purchase Flow**
- [ ] Update Credits page purchase buttons:
  ```tsx
  import { paymentService } from '@/lib/services/payment.service'

  const handlePurchase = async (amount: number) => {
    try {
      setLoading(true)
      const session = await paymentService.purchaseCredits(amount)
      // Redirect to Checkout.com hosted page
      window.location.href = session.checkout_url
    } catch (error) {
      toast({
        title: 'Error',
        message: 'Failed to initiate payment',
        type: 'error'
      })
    } finally {
      setLoading(false)
    }
  }
  ```
- [ ] Add loading states to purchase buttons
- [ ] Show confirmation dialog before redirect
- [ ] Handle payment success callback (return URL)

**4.4 Create Payment Success/Cancel Pages**
- [ ] Create `frontend/src/app/dashboard/credits/payment-success/page.tsx`:
  - [ ] Show success message
  - [ ] Display purchased credits
  - [ ] Button: "View Credits" → `/dashboard/credits`
  - [ ] Confetti or celebration animation
- [ ] Create `frontend/src/app/dashboard/credits/payment-cancel/page.tsx`:
  - [ ] Show cancellation message
  - [ ] Button: "Try Again" → `/dashboard/credits`
  - [ ] Button: "Contact Support" → `/contact`

**4.5 Implement Pro Subscription Flow**
- [ ] Update Pricing page CTA buttons:
  ```tsx
  import { paymentService } from '@/lib/services/payment.service'
  import { useAuth } from '@/lib/hooks/useAuth'

  const handleUpgrade = async () => {
    if (!user) {
      router.push('/login?redirect=/pricing')
      return
    }

    try {
      setLoading(true)
      const session = await paymentService.subscribeToPro()
      window.location.href = session.checkout_url
    } catch (error) {
      toast({ title: 'Error', message: 'Failed to start subscription', type: 'error' })
    } finally {
      setLoading(false)
    }
  }
  ```
- [ ] Show "Upgrade to Pro" button only for free users
- [ ] Show "Current Plan" badge for Pro users
- [ ] Test complete flow: Click upgrade → Redirect → (Mock payment) → Success page

**4.6 Create Subscription Success Page**
- [ ] Create `frontend/src/app/dashboard/subscription/success/page.tsx`:
  - [ ] Welcome to Pro message
  - [ ] List of unlocked features
  - [ ] Button: "Go to Dashboard" → `/dashboard`
  - [ ] Celebration animation

---

## Phase 5: Google OAuth Integration

**5.1 Research Backend OAuth Implementation**
- [ ] Locate backend OAuth routes (likely `/api/v1/auth/google/*`)
- [ ] Identify endpoints:
  - [ ] Initiate OAuth flow (redirect to Google)
  - [ ] OAuth callback handler
  - [ ] Token exchange endpoint
- [ ] Document required environment variables (Client ID, Client Secret, Redirect URI)
- [ ] Check session/token management strategy

**5.2 Create OAuth Service**
- [ ] Create `frontend/src/lib/services/oauth.service.ts`:
  ```tsx
  export const oauthService = {
    initiateGoogleLogin(redirectTo?: string) {
      const params = new URLSearchParams()
      if (redirectTo) params.append('redirect', redirectTo)

      // Redirect to backend OAuth initiation endpoint
      window.location.href = `/api/v1/auth/google?${params.toString()}`
    },

    async handleCallback(code: string, state?: string) {
      // Backend will handle this, frontend just needs to show loading
      // Backend redirects to /dashboard after success
    }
  }
  ```

**5.3 Create Login Page**
- [ ] Create `frontend/src/app/login/page.tsx`:
  - [ ] Show Perpetua logo and tagline
  - [ ] "Sign in with Google" button (prominent, branded)
  - [ ] Optional: Email/password form (if also implemented)
  - [ ] Link to Privacy Policy and Terms
  - [ ] Loading state while redirecting
- [ ] Style to match dark theme of public pages
- [ ] Make responsive

**5.4 Update Public Navigation**
- [ ] Add "Login" button to public page header:
  - [ ] Update [page.tsx](frontend/src/app/page.tsx) navigation (line 159-211)
  - [ ] Add "Login" link next to "Get Started"
  - [ ] Link to `/login`
- [ ] Update Footer with login link (optional)

**5.5 Implement OAuth Callback Handler**
- [ ] Create `frontend/src/app/auth/callback/page.tsx`:
  ```tsx
  'use client'
  import { useEffect } from 'react'
  import { useRouter, useSearchParams } from 'next/navigation'
  import { useAuth } from '@/lib/hooks/useAuth'

  export default function AuthCallback() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const { refetch } = useAuth()

    useEffect(() => {
      // Backend sets session cookie, verify authentication
      refetch().then(() => {
        const redirect = searchParams.get('redirect') || '/dashboard'
        router.push(redirect)
      }).catch(() => {
        router.push('/login?error=auth_failed')
      })
    }, [])

    return <div>Completing sign in...</div>
  }
  ```
- [ ] Show loading spinner
- [ ] Handle error states (invalid code, expired session)

**5.6 Update Auth Context**
- [ ] Update `frontend/src/lib/contexts/AuthContext.tsx`:
  - [ ] Add `loginWithGoogle` function
  - [ ] Handle OAuth session cookies
  - [ ] Update user fetch logic to work with OAuth tokens
  - [ ] Add logout function (clear session)
- [ ] Update `useAuth` hook to expose OAuth functions

**5.7 Protect Dashboard Routes**
- [ ] Add auth check to dashboard layout:
  ```tsx
  // frontend/src/app/dashboard/layout.tsx
  import { useAuth } from '@/lib/hooks/useAuth'
  import { useRouter } from 'next/navigation'

  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login?redirect=/dashboard')
    }
  }, [user, isLoading])
  ```
- [ ] Show loading state while checking auth
- [ ] Test: Access dashboard without login → Redirect to login

**5.8 Add Logout Functionality**
- [ ] Update [ProfilePopover.tsx](frontend/src/components/layout/ProfilePopover.tsx) logout (line 32-36):
  ```tsx
  import { useAuth } from '@/lib/hooks/useAuth'

  const { logout } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      toast({ title: 'Error', message: 'Failed to log out', type: 'error' })
    }
  }
  ```
- [ ] Clear all client-side state on logout
- [ ] Test full flow: Login → Use app → Logout → Redirect to login

---

## Phase 6: Achievements System

**6.1 Fetch Achievements from Backend**
- [ ] Locate backend achievements endpoint (likely `/api/v1/achievements`)
- [ ] Document achievement data structure:
  ```tsx
  interface Achievement {
    id: string
    name: string
    description: string
    icon: string
    category: string
    unlocked: boolean
    unlocked_at?: string
    progress?: number
    total_required?: number
  }
  ```

**6.2 Update Achievement Hook**
- [ ] Update `frontend/src/lib/hooks/useAchievements.ts`:
  ```tsx
  import { useQuery } from '@tanstack/react-query'
  import { apiClient } from '@/lib/api/client'

  export function useAchievements() {
    return useQuery({
      queryKey: ['achievements'],
      queryFn: () => apiClient.get<{ data: Achievement[] }>('/achievements'),
    })
  }

  export function useAchievementStats() {
    return useQuery({
      queryKey: ['achievements', 'stats'],
      queryFn: () => apiClient.get<{ data: { total: number, unlocked: number } }>('/achievements/stats'),
    })
  }
  ```

**6.3 Update Achievements Page**
- [ ] Open [achievements/page.tsx](frontend/src/app/dashboard/achievements/page.tsx)
- [ ] Replace mock data with `useAchievements()` hook
- [ ] Display all achievements (locked and unlocked):
  - [ ] Unlocked: Full color, show unlock date
  - [ ] Locked: Grayscale/low opacity, show progress bar if applicable
  - [ ] Group by category (optional)
- [ ] Add filters:
  - [ ] "All", "Unlocked", "Locked"
  - [ ] Category filter (Tasks, Streaks, Focus, etc.)
- [ ] Add search functionality
- [ ] Show achievement stats at top:
  - [ ] "X of Y achievements unlocked"
  - [ ] Progress bar

**6.4 Create Achievement Detail Modal**
- [ ] Create `frontend/src/components/achievements/AchievementDetail.tsx`:
  - [ ] Show large achievement icon
  - [ ] Name and description
  - [ ] Unlock date (if unlocked)
  - [ ] Progress towards next achievement (if locked)
  - [ ] Tips on how to unlock
  - [ ] Share button (optional)
- [ ] Open modal when achievement is clicked

**6.5 Add Achievement Notifications**
- [ ] Create achievement unlock notification:
  ```tsx
  // When new achievement is unlocked (via WebSocket or polling)
  toast({
    title: '🏆 Achievement Unlocked!',
    message: achievement.name,
    type: 'success',
    duration: 5000,
  })
  ```
- [ ] Consider confetti animation on unlock
- [ ] Add to notifications dropdown

**6.6 Add Achievement Badges to Profile**
- [ ] Update profile page to show recent achievements
- [ ] Display top 3-5 achievements as badges
- [ ] Add "View All" button linking to `/dashboard/achievements`

---

## Testing Checklist

### Phase 1 Testing
- [ ] All public pages load without errors
- [ ] Free tier messaging is prominent and clear
- [ ] Pricing comparison table is readable on mobile
- [ ] Legal pages (Privacy, ToS) display correctly
- [ ] Footer links work (Privacy, Terms, Open Source)

### Phase 2 Testing
- [ ] Sidebar toggles work on desktop and mobile
- [ ] Mobile sidebar overlays content (doesn't push)
- [ ] Hamburger menu appears on mobile
- [ ] Settings back buttons navigate correctly
- [ ] Onboarding replay works
- [ ] Notes archive moved to settings
- [ ] "+ New" dropdown creates notes
- [ ] Credits button navigates to credits page
- [ ] Profile displays plan (Free/Pro), no email
- [ ] Help & Support links to contact

### Phase 3 Testing
- [ ] Credits page displays balance and transactions
- [ ] Credit packages display correctly
- [ ] Purchase button initiates checkout (mock)

### Phase 4 Testing
- [ ] Payment flow redirects to Checkout.com
- [ ] Success page displays after payment
- [ ] Cancel page works
- [ ] Pro subscription flow completes
- [ ] Credits update after purchase

### Phase 5 Testing
- [ ] Login page displays Google button
- [ ] OAuth flow redirects correctly
- [ ] User lands on dashboard after login
- [ ] Dashboard protected (redirects if not logged in)
- [ ] Logout works, clears session

### Phase 6 Testing
- [ ] Achievements fetch from backend
- [ ] All achievements display (locked + unlocked)
- [ ] Achievement detail modal works
- [ ] Filters and search work
- [ ] Progress bars display for locked achievements

---

## Notes

### Backend Assumptions
- Checkout.com integration is complete and tested
- Google OAuth endpoints are functional
- Credits API endpoints exist and return correct data
- Achievements API exists and returns all achievements with unlock status

### Design Consistency
- All new pages should match the dark theme (gray-950 background)
- Use existing component library (Button, Input, Toast, etc.)
- Follow spacing and typography patterns from existing pages
- Ensure mobile responsiveness for all new components

### Accessibility
- Maintain WCAG compliance (ARIA labels, keyboard navigation)
- Test with screen readers
- Ensure sufficient color contrast
- Support reduced motion preferences

### Performance
- Lazy load heavy components (modals, charts)
- Implement pagination for long lists (transactions, achievements)
- Use React Query caching to minimize API calls
- Optimize images (use Next.js Image component)

---

## Dependencies to Install

```bash
# If not already present
npm install driver.js  # For onboarding tour (already installed)
npm install @tanstack/react-query  # For data fetching (already installed)
npm install zod  # For schemas (already installed)
```

---

## Completion Tracking

**Phase 1**: [X] 10/10 tasks complete
**Phase 2**: [ ] 0/13 tasks complete
**Phase 3**: [ ] 0/4 tasks complete
**Phase 4**: [ ] 0/6 tasks complete
**Phase 5**: [ ] 0/8 tasks complete
**Phase 6**: [ ] 0/6 tasks complete

**Overall Progress**: 10/47 tasks complete (21%)

---

**Last Updated**: 2026-02-09
**Status**: Ready for implementation
