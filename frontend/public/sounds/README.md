# Notification Sounds

This directory contains sound files for notification alerts.

## Required Files

To enable notification sounds, add the following sound files to this directory:

- `notification.mp3` - Default notification sound
- `notification-gentle.mp3` - Gentle notification sound (optional)
- `notification-urgent.mp3` - Urgent notification sound (optional)

## Sound File Requirements

- **Format**: MP3 (recommended for broad browser support)
- **Duration**: 1-3 seconds (keep notifications brief)
- **File Size**: < 100KB (keep files small for fast loading)
- **Volume**: Normalized to prevent overly loud notifications

## Free Sound Resources

You can find free notification sounds at:
- [Notification Sounds](https://notificationsounds.com/)
- [Zapsplat](https://www.zapsplat.com/sound-effect-category/notification/)
- [Freesound](https://freesound.org/search/?q=notification)

## Usage

Sounds are automatically played by the `ServiceWorkerListener` component when browser notifications are shown. See `src/lib/config/notification-sounds.ts` for configuration.

## Testing

To test notification sounds without waiting for a reminder:
1. Add sound files to this directory
2. Open browser console
3. Run: `new Audio('/sounds/notification.mp3').play()`
