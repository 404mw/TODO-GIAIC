// Service Worker for reminder notifications
// Polls backend API every 60 seconds to check for due reminders
// Per research.md Section 15 and tasks.md T091-T096

const SW_VERSION = '1.0.3';
const POLL_INTERVAL = 60000; // 60 seconds

// API URL - configured via postMessage from the app (which has access to NEXT_PUBLIC_API_URL)
// Falls back to localhost for development if not set
let API_BASE_URL = 'http://localhost:8000/api/v1';

// Install event
self.addEventListener('install', (event) => {
  console.log(`[SW ${SW_VERSION}] Installing...`);
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log(`[SW ${SW_VERSION}] Activating...`);
  event.waitUntil(clients.claim());
});

// Fetch reminders from backend API
async function fetchRemindersFromBackend() {
  try {
    // TODO: Get auth token from client via postMessage or IndexedDB
    const response = await fetch(`${API_BASE_URL}/reminders`);
    if (!response.ok) {
      console.warn('[SW] Failed to fetch reminders:', response.status);
      return [];
    }
    const data = await response.json();
    // Backend returns {data: [...], pagination: {...}}
    return data.data || [];
  } catch (error) {
    console.error('[SW] Error fetching reminders:', error);
    return [];
  }
}

// Fetch tasks from backend API
async function fetchTasksFromBackend() {
  try {
    // TODO: Get auth token from client via postMessage or IndexedDB
    const response = await fetch(`${API_BASE_URL}/tasks`);
    if (!response.ok) {
      console.warn('[SW] Failed to fetch tasks:', response.status);
      return [];
    }
    const data = await response.json();
    // Backend returns {data: [...], pagination: {...}}
    return data.data || [];
  } catch (error) {
    console.error('[SW] Error fetching tasks:', error);
    return [];
  }
}

// Calculate reminder trigger time
// Per research.md Section 15 - matches frontend date.ts utility
function calculateReminderTriggerTime(reminder, task) {
  // Backend uses snake_case: due_date
  if (!task.due_date) return null;

  const dueDate = new Date(task.due_date);

  // Validate date is valid
  if (isNaN(dueDate.getTime())) return null;

  // Backend uses scheduled_at for absolute reminders or offset_minutes for relative
  if (reminder.type === 'absolute' && reminder.scheduled_at) {
    return new Date(reminder.scheduled_at);
  } else if (reminder.offset_minutes != null) {
    // offset_minutes is negative for "before" (e.g., -15 = 15 minutes before)
    const offsetMs = reminder.offset_minutes * 60 * 1000;
    return new Date(dueDate.getTime() + offsetMs);
  }

  return null;
}

// Check for due reminders and send notifications
async function checkReminders() {
  const now = new Date();
  const reminders = await fetchRemindersFromBackend();
  const tasks = await fetchTasksFromBackend();

  const dueReminders = reminders.filter((reminder) => {
    // Skip already fired reminders (T100)
    if (reminder.fired) return false;

    // Backend uses snake_case: task_id
    const task = tasks.find((t) => t.id === reminder.task_id);
    if (!task) return false;

    const triggerTime = calculateReminderTriggerTime(reminder, task);
    return triggerTime && triggerTime <= now;
  });

  for (const reminder of dueReminders) {
    const task = tasks.find((t) => t.id === reminder.task_id);
    if (!task) continue;

    // T095: Browser notification (if permission granted)
    // Dual notification system - always try both browser + in-app
    let browserNotificationSent = false;
    if (self.Notification && Notification.permission === 'granted') {
      try {
        // Reminder type can be 'absolute' or 'relative', display generic message
        const reminderTitle = `Task Reminder: ${task.title}`;
        await self.registration.showNotification(reminderTitle, {
          body: task.description || 'You have a task due soon',
          icon: '/icon-192.png',
          tag: reminder.id,
          requireInteraction: true,
          data: {
            url: `/dashboard/tasks/${task.id}`,
          },
        });
        browserNotificationSent = true;
      } catch (error) {
        console.error('[SW] Error showing browser notification:', error);
      }
    }

    // T096: In-app toast (postMessage to all clients)
    // Always send toast (part of dual notification system)
    const allClients = await clients.matchAll({ includeUncontrolled: true });
    allClients.forEach((client) => {
      client.postMessage({
        type: 'REMINDER_DUE',
        reminder,
        task,
        fallbackToast: !browserNotificationSent, // Indicate if browser notification failed
      });
    });

    // Mark reminder as delivered
    try {
      // TODO: Get auth token and include in headers
      await fetch(`${API_BASE_URL}/reminders/${reminder.id}/fire`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      console.error('[SW] Error marking reminder as delivered:', error);
    }
  }
}

// Start polling for reminders
let pollInterval;

self.addEventListener('message', (event) => {
  // Configure API URL (sent from app which has access to NEXT_PUBLIC_API_URL)
  if (event.data && event.data.type === 'SET_API_URL') {
    API_BASE_URL = event.data.url;
    console.log('[SW] API URL configured:', API_BASE_URL);
  }

  if (event.data && event.data.type === 'START_REMINDER_POLLING') {
    console.log('[SW] Starting reminder polling...');

    // Clear any existing interval
    if (pollInterval) {
      clearInterval(pollInterval);
    }

    // Start new polling interval
    pollInterval = setInterval(checkReminders, POLL_INTERVAL);

    // Check immediately
    checkReminders();
  }

  if (event.data && event.data.type === 'STOP_REMINDER_POLLING') {
    console.log('[SW] Stopping reminder polling...');
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const urlToOpen = event.notification.data?.url || '/dashboard/tasks';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Check if there's already a window open
      for (const client of clientList) {
        if (client.url.includes('/dashboard') && 'focus' in client) {
          client.focus();
          client.navigate(urlToOpen);
          return;
        }
      }

      // No window found, open a new one
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});
