// Service Worker for reminder notifications
// Polls MSW every 60 seconds to check for due reminders
// Per research.md Section 15 and tasks.md T091-T096

const SW_VERSION = '1.0.1';
const POLL_INTERVAL = 60000; // 60 seconds

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

// Fetch reminders from MSW
async function fetchRemindersFromMSW() {
  try {
    const response = await fetch('/api/reminders');
    if (!response.ok) throw new Error('Failed to fetch reminders');
    const data = await response.json();
    return data.reminders || [];
  } catch (error) {
    console.error('[SW] Error fetching reminders:', error);
    return [];
  }
}

// Fetch tasks from MSW
async function fetchTasksFromMSW() {
  try {
    const response = await fetch('/api/tasks');
    if (!response.ok) throw new Error('Failed to fetch tasks');
    const data = await response.json();
    return data.tasks || [];
  } catch (error) {
    console.error('[SW] Error fetching tasks:', error);
    return [];
  }
}

// Calculate reminder trigger time
// Per research.md Section 15 - matches frontend date.ts utility
function calculateReminderTriggerTime(reminder, task) {
  if (!task.dueDate) return null;

  const dueDate = new Date(task.dueDate);

  // Validate date is valid
  if (isNaN(dueDate.getTime())) return null;

  // offsetMinutes is negative for "before" (e.g., -15 = 15 minutes before)
  const offsetMs = reminder.offsetMinutes * 60 * 1000;
  return new Date(dueDate.getTime() + offsetMs);
}

// Check for due reminders and send notifications
async function checkReminders() {
  const now = new Date();
  const reminders = await fetchRemindersFromMSW();
  const tasks = await fetchTasksFromMSW();

  const dueReminders = reminders.filter((reminder) => {
    // Skip already delivered reminders (T100)
    if (reminder.delivered) return false;

    const task = tasks.find((t) => t.id === reminder.taskId);
    if (!task) return false;

    const triggerTime = calculateReminderTriggerTime(reminder, task);
    return triggerTime && triggerTime <= now;
  });

  for (const reminder of dueReminders) {
    const task = tasks.find((t) => t.id === reminder.taskId);

    // T095: Browser notification (if permission granted)
    // Dual notification system - always try both browser + in-app
    let browserNotificationSent = false;
    if (self.Notification && Notification.permission === 'granted') {
      try {
        await self.registration.showNotification(reminder.title, {
          body: task.title,
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
      await fetch(`/api/reminders/${reminder.id}/delivered`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('[SW] Error marking reminder as delivered:', error);
    }
  }
}

// Start polling for reminders
let pollInterval;

self.addEventListener('message', (event) => {
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
