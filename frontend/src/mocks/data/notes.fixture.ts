import type { Note } from '@/lib/schemas/note.schema'

// Sample note fixtures for MSW
export const notesFixture: Note[] = [
  {
    id: '880e8400-e29b-41d4-a716-446655440001',
    content: 'Remember to follow up with the client about the budget revisions. They mentioned wanting to cut costs by 15%.',
    archived: false,
    voiceUrl: null,
    voiceDurationSeconds: null,
    transcriptionStatus: null,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440002',
    content: 'Ideas for improving onboarding: add interactive tutorials, gamify first tasks, provide video walkthroughs',
    archived: false,
    voiceUrl: null,
    voiceDurationSeconds: null,
    transcriptionStatus: null,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440003',
    content: 'Call mom tomorrow to discuss holiday plans. She wants to book the cabin early this year.',
    archived: false,
    voiceUrl: 'https://example.com/voice/note-003.mp3',
    voiceDurationSeconds: 8,
    transcriptionStatus: 'completed',
    createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
    updatedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440004',
    content: 'Bug found: authentication token expires too quickly on mobile. Need to investigate session management.',
    archived: false,
    voiceUrl: null,
    voiceDurationSeconds: null,
    transcriptionStatus: null,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '880e8400-e29b-41d4-a716-446655440005',
    content: 'Meeting notes from standup: Team agreed to move sprint planning to Tuesdays. Sprint velocity looking good.',
    archived: true, // Example of archived note
    voiceUrl: null,
    voiceDurationSeconds: null,
    transcriptionStatus: null,
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 1 week ago
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
]
