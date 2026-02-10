import type { User } from '@/lib/schemas/user.schema'

// Sample user fixture for MSW
export const userFixture: User = {
  id: '990e8400-e29b-41d4-a716-446655440001',
  google_id: 'google-oauth-id-123456',
  email: 'alex.johnson@example.com',
  name: 'Alex Johnson',
  avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
  timezone: 'America/New_York',
  tier: 'free',
  created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days ago
  updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
}
