export const LIMITS = {
  // Task limits
  MAX_TITLE_LENGTH: 200,
  MAX_DESCRIPTION_LENGTH: 2000,
  MAX_TAGS: 10,
  MAX_TAG_LENGTH: 30,
  MAX_SUBTASKS_PER_TASK: 50,
  MAX_TASKS_PER_USER: 1000,

  // Note limits
  MAX_NOTES_PER_TASK: 100,
  MAX_NOTE_LENGTH: 5000,

  // Reminder limits
  MAX_REMINDERS_PER_USER: 100,

  // AI Credit limits (Free tier)
  DAILY_FREE_CREDITS: 10,

  // AI Credit limits (Pro tier)
  MONTHLY_PRO_CREDITS: 500,
  MAX_CARRY_OVER_CREDITS: 50,

  // AI Credit costs
  CREDIT_COST_CHAT: 1,
  CREDIT_COST_SUBTASK_GEN: 1,
  CREDIT_COST_NOTE_CONVERT: 1,
  CREDIT_COST_VOICE_PER_MINUTE: 5,

  // Focus session
  MAX_FOCUS_DURATION_MINUTES: 240, // 4 hours
} as const;

export type LimitKey = keyof typeof LIMITS;
