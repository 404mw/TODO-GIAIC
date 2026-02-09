import type { Reminder } from '@/lib/schemas/reminder.schema'

const MOCK_USER_ID = '00000000-0000-0000-0000-000000000001'

// Sample reminder fixtures for MSW
export const remindersFixture: Reminder[] = [
  {
    id: '660e8400-e29b-41d4-a716-446655440001',
    task_id: '550e8400-e29b-41d4-a716-446655440005', // Prepare presentation slides
    user_id: MOCK_USER_ID,
    type: 'before',
    offset_minutes: -1440, // 1 day before due date
    method: 'in_app',
    scheduled_at: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day from now
    fired: false,
    fired_at: null,
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '660e8400-e29b-41d4-a716-446655440002',
    task_id: '550e8400-e29b-41d4-a716-446655440001', // Finish project proposal
    user_id: MOCK_USER_ID,
    type: 'before',
    offset_minutes: -15, // 15 minutes before due date
    method: 'in_app',
    scheduled_at: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
    fired: false,
    fired_at: null,
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '660e8400-e29b-41d4-a716-446655440003',
    task_id: '550e8400-e29b-41d4-a716-446655440007', // Call insurance company
    user_id: MOCK_USER_ID,
    type: 'before',
    offset_minutes: -60, // 1 hour before due date
    method: 'in_app',
    scheduled_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30 minutes from now
    fired: false,
    fired_at: null,
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
]
