import { http, HttpResponse, delay } from 'msw'
import type { User } from '@/lib/schemas/user.schema'
import { UpdateUserRequestSchema } from '@/lib/schemas/user.schema'
import { userFixture } from '../data/user.fixture'

// In-memory storage (single user profile)
let userProfile: User = { ...userFixture }

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// GET /api/user/profile - Get user profile
export const getUserProfileHandler = http.get('/api/user/profile', async () => {
  await simulateLatency()

  return HttpResponse.json(userProfile, { status: 200 })
})

// PATCH /api/user/profile - Update user profile
export const updateUserProfileHandler = http.patch('/api/user/profile', async ({ request }) => {
  await simulateLatency()

  const body = await request.json()

  try {
    UpdateUserRequestSchema.parse(body)

    userProfile = {
      ...userProfile,
      ...(body as any),
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(userProfile, { status: 200 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid profile update data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// PATCH /api/user/preferences - Update user preferences
export const updateUserPreferencesHandler = http.patch(
  '/api/user/preferences',
  async ({ request }) => {
    await simulateLatency()

    const body = await request.json()

    try {
      // Update user profile
      userProfile = {
        ...userProfile,
        ...(body as any),
        updated_at: new Date().toISOString(),
      }

      return HttpResponse.json({ data: userProfile }, { status: 200 })
    } catch (error) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid preferences data',
            details: error,
          },
        },
        { status: 400 }
      )
    }
  }
)

// PATCH /api/user/theme - Update theme tweaks
export const updateThemeTweaksHandler = http.patch('/api/user/theme', async ({ request }) => {
  await simulateLatency()

  const body = await request.json()

  try {
    // Theme tweaks not implemented yet - just return success
    userProfile.updated_at = new Date().toISOString()

    return HttpResponse.json({ data: userProfile }, { status: 200 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid theme data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// POST /api/user/complete-tutorial - Mark tutorial as completed
export const completeTutorialHandler = http.post('/api/user/complete-tutorial', async () => {
  await simulateLatency()

  userProfile.updated_at = new Date().toISOString()

  return HttpResponse.json({ data: userProfile }, { status: 200 })
})

// Export all user profile handlers
export const userHandlers = [
  getUserProfileHandler,
  updateUserProfileHandler,
  updateUserPreferencesHandler,
  updateThemeTweaksHandler,
  completeTutorialHandler,
]
