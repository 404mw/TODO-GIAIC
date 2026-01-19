import type { Reminder } from '@/lib/schemas/reminder.schema'

// Sample reminder fixtures for MSW
export const remindersFixture: Reminder[] = [
  {
    id: '660e8400-e29b-41d4-a716-446655440001',
    taskId: '550e8400-e29b-41d4-a716-446655440005', // Prepare presentation slides
    title: 'Presentation reminder',
    timing: {
      type: 'relative_to_due_date',
      offsetMinutes: -1440, // 1 day before due date
    },
    deliveryMethod: 'both',
    enabled: true,
    delivered: false,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '660e8400-e29b-41d4-a716-446655440002',
    taskId: '550e8400-e29b-41d4-a716-446655440001', // Finish project proposal
    title: 'Proposal deadline approaching',
    timing: {
      type: 'relative_to_due_date',
      offsetMinutes: -15, // 15 minutes before due date
    },
    deliveryMethod: 'both',
    enabled: true,
    delivered: false,
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '660e8400-e29b-41d4-a716-446655440003',
    taskId: '550e8400-e29b-41d4-a716-446655440007', // Call insurance company
    title: 'Call insurance',
    timing: {
      type: 'relative_to_due_date',
      offsetMinutes: -60, // 1 hour before due date
    },
    deliveryMethod: 'both',
    enabled: true,
    delivered: false,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
]
