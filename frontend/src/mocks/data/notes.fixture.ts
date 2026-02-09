import type { Note } from '@/lib/schemas/note.schema'

const MOCK_USER_ID = '00000000-0000-0000-0000-000000000001'

// Sample note fixtures for MSW
export const notesFixture: Note[] = [
  {
    id: '880e8400-e29b-41d4-a716-446655440001',
    user_id: MOCK_USER_ID,
    content: 'Remember to follow up with the client about the budget revisions. They mentioned wanting to cut costs by 15%.',
    archived: false,
    voice_url: null,
    voice_duration_seconds: null,
    transcription_status: null,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440002',
    user_id: MOCK_USER_ID,
    content: 'Ideas for improving onboarding: add interactive tutorials, gamify first tasks, provide video walkthroughs',
    archived: false,
    voice_url: null,
    voice_duration_seconds: null,
    transcription_status: null,
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440003',
    user_id: MOCK_USER_ID,
    content: 'Call mom tomorrow to discuss holiday plans. She wants to book the cabin early this year.',
    archived: false,
    voice_url: '/mock/voice/note003.mp3',
    voice_duration_seconds: 8,
    transcription_status: 'completed',
    created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
    updated_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440004',
    user_id: MOCK_USER_ID,
    content: 'Bug found: authentication token expires too quickly on mobile. Need to investigate session management.',
    archived: false,
    voice_url: null,
    voice_duration_seconds: null,
    transcription_status: null,
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
    updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440005',
    user_id: MOCK_USER_ID,
    content: 'Meeting notes from standup: Team agreed to move sprint planning to Tuesdays. Sprint velocity looking good.',
    archived: true, // Example of archived note
    voice_url: null,
    voice_duration_seconds: null,
    transcription_status: null,
    created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 1 week ago
    updated_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
]
