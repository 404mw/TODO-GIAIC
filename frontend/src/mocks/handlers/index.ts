import { tasksHandlers } from './tasks.handlers'
import { notesHandlers } from './notes.handlers'
import { remindersHandlers } from './reminders.handlers'
import { achievementsHandlers } from './achievements.handlers'
import { searchHandlers } from './search.handlers'
import { aiHandlers } from './ai.handlers'
import { userHandlers } from './user.handlers'

// Combine all handlers for MSW
export const handlers = [
  ...tasksHandlers,
  ...notesHandlers,
  ...remindersHandlers,
  ...achievementsHandlers,
  ...searchHandlers,
  ...aiHandlers,
  ...userHandlers,
]
