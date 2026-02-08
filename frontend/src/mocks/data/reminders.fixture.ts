import type { Reminder } from '@/lib/schemas/reminder.schema'

// Sample reminder fixtures for MSW
export const remindersFixture: Reminder[] = [
  {
    id: '660e8400-e29b-41d4-a716-446655440001',
    taskId: '550e8400-e29b-41d4-a716-446655440005', // Prepare presentation slides
    type: 'before',
    offsetMinutes: 1440, // 1 day before
    scheduledAt: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days from now
    method: 'in_app',
    fired: false,
    firedAt: null,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '660e8400-e29b-41d4-a716-446655440002',
    taskId: '550e8400-e29b-41d4-a716-446655440001', // Finish project proposal
    type: 'before',
    offsetMinutes: 15, // 15 minutes before
    scheduledAt: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(), // 1 hour from now
    method: 'push',
    fired: false,
    firedAt: null,
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '660e8400-e29b-41d4-a716-446655440003',
    taskId: '550e8400-e29b-41d4-a716-446655440007', // Call insurance company
    type: 'before',
    offsetMinutes: 60, // 1 hour before
    scheduledAt: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), // 3 hours from now
    method: 'email',
    fired: false,
    firedAt: null,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
]
