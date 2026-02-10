'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Button } from '@/components/ui/Button'

interface FocusTimerProps {
  durationMinutes: number
  onComplete?: () => void
  onPause?: () => void
  onResume?: () => void
  onExit?: () => void // T127: For keyboard exit
  isRunning?: boolean
}

export function FocusTimer({
  durationMinutes,
  onComplete,
  onPause,
  onResume,
  onExit,
  isRunning = true,
}: FocusTimerProps) {
  const [timeRemaining, setTimeRemaining] = useState(durationMinutes * 60)
  const [isPaused, setIsPaused] = useState(!isRunning)
  const [isCompleted, setIsCompleted] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Calculate progress percentage
  const progress = ((durationMinutes * 60 - timeRemaining) / (durationMinutes * 60)) * 100

  // T126: Play completion sound
  const playCompletionSound = useCallback(() => {
    try {
      if (!audioRef.current) {
        audioRef.current = new Audio('/sounds/notification.mp3')
      }
      audioRef.current.currentTime = 0
      audioRef.current.play().catch((e) => {
        console.warn('Could not play completion sound:', e)
      })
    } catch (error) {
      console.warn('Audio playback not supported:', error)
    }
  }, [])

  // T126: Show browser notification
  const showCompletionNotification = useCallback(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification('Focus Session Complete!', {
          body: 'Great work! You completed your focus session.',
          icon: '/icon-192.png',
          tag: 'focus-complete',
          requireInteraction: true,
        })
      }
    }
  }, [])

  // Timer logic
  useEffect(() => {
    if (isPaused || isCompleted) return

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          setIsCompleted(true)
          // T126: Audio/visual alert at countdown zero
          playCompletionSound()
          showCompletionNotification()
          onComplete?.()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isPaused, isCompleted, onComplete, playCompletionSound, showCompletionNotification])

  const handlePause = useCallback(() => {
    setIsPaused(true)
    onPause?.()
  }, [onPause])

  const handleResume = useCallback(() => {
    setIsPaused(false)
    onResume?.()
  }, [onResume])

  const handleReset = useCallback(() => {
    setTimeRemaining(durationMinutes * 60)
    setIsCompleted(false)
    setIsPaused(true)
  }, [durationMinutes])

  // T127: Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape to exit Focus Mode
      if (e.key === 'Escape') {
        e.preventDefault()
        onExit?.()
      }
      // Space to pause/resume
      if (e.key === ' ' && !isCompleted) {
        e.preventDefault()
        if (isPaused) {
          handleResume()
        } else {
          handlePause()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isPaused, isCompleted, onExit, handlePause, handleResume])

  // Calculate ring stroke
  const radius = 90
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (progress / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Timer ring */}
      <div className="relative">
        <svg
          className="h-64 w-64 -rotate-90 transform"
          viewBox="0 0 200 200"
        >
          {/* Background ring */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200 dark:text-gray-700"
          />
          {/* Progress ring */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={[
              'transition-all duration-1000 ease-linear',
              isCompleted
                ? 'text-green-500'
                : isPaused
                ? 'text-yellow-500'
                : 'text-blue-500',
            ].join(' ')}
          />
        </svg>
        {/* Timer display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold text-gray-900 dark:text-gray-100">
            {formatTime(timeRemaining)}
          </span>
          <span className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {isCompleted
              ? 'Complete!'
              : isPaused
              ? 'Paused'
              : 'Focusing...'}
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-3">
        {!isCompleted && (
          <>
            {isPaused ? (
              <Button onClick={handleResume} className="min-w-24">
                Resume
              </Button>
            ) : (
              <Button onClick={handlePause} variant="outline" className="min-w-24">
                Pause
              </Button>
            )}
          </>
        )}
        <Button onClick={handleReset} variant="outline" className="min-w-24">
          Reset
        </Button>
      </div>

      {/* Progress info */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        <p>
          {Math.round(progress)}% complete
        </p>
        <p className="mt-1">
          {Math.floor((durationMinutes * 60 - timeRemaining) / 60)} of {durationMinutes} minutes elapsed
        </p>
      </div>
    </div>
  )
}
