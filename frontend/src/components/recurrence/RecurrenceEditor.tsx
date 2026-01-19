/**
 * RecurrenceEditor Component (FR-069, FR-073)
 * Task: T108, T110, T114
 * Phase: 6 - US1 Extended - Recurrence
 *
 * Allows users to configure task recurrence with:
 * - Preset buttons for quick setup (Daily, Weekly, Monthly, Custom) (T114)
 * - Frequency selection (DAILY, WEEKLY, MONTHLY)
 * - Custom interval input
 * - Weekday selection for weekly recurrence
 * - Human-readable preview
 */

'use client';

import { useState, useMemo } from 'react';
import { createRRuleString, getRecurrenceDescription } from '@/lib/utils/recurrence';

export interface RecurrenceEditorProps {
  value?: {
    enabled: boolean;
    rule: string;
    timezone?: string;
    instanceGenerationMode?: 'on_completion';
    humanReadable: string;
  };
  onChange: (recurrence: {
    enabled: boolean;
    rule: string;
    timezone: string;
    instanceGenerationMode: 'on_completion';
    humanReadable: string;
  } | undefined) => void;
}

const WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

// T114: Preset configurations for quick recurrence setup
type PresetType = 'daily' | 'weekly' | 'monthly' | 'custom';

const RECURRENCE_PRESETS: Record<PresetType, { frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY'; interval: number; label: string }> = {
  daily: { frequency: 'DAILY', interval: 1, label: 'Daily' },
  weekly: { frequency: 'WEEKLY', interval: 1, label: 'Weekly' },
  monthly: { frequency: 'MONTHLY', interval: 1, label: 'Monthly' },
  custom: { frequency: 'WEEKLY', interval: 1, label: 'Custom' },
};

export function RecurrenceEditor({ value, onChange }: RecurrenceEditorProps) {
  const [enabled, setEnabled] = useState(value?.enabled ?? false);
  const [frequency, setFrequency] = useState<'DAILY' | 'WEEKLY' | 'MONTHLY'>('WEEKLY');
  const [interval, setInterval] = useState(1);
  const [selectedWeekdays, setSelectedWeekdays] = useState<number[]>([0]); // Default: Monday
  const [activePreset, setActivePreset] = useState<PresetType>('weekly'); // T114: Track active preset
  const [showCustomOptions, setShowCustomOptions] = useState(false); // T114: Show custom options when custom is selected

  // Generate RRule string from current settings
  const ruleString = useMemo(() => {
    return createRRuleString({
      frequency,
      interval,
      byweekday: frequency === 'WEEKLY' ? selectedWeekdays : undefined,
    });
  }, [frequency, interval, selectedWeekdays]);

  // Generate human-readable description
  const humanReadable = useMemo(() => {
    return getRecurrenceDescription(ruleString);
  }, [ruleString]);

  // Handle enable/disable toggle
  const handleToggle = (checked: boolean) => {
    setEnabled(checked);

    if (!checked) {
      // Disable recurrence
      onChange(undefined);
    } else {
      // Enable with current settings
      onChange({
        enabled: true,
        rule: ruleString,
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable,
      });
    }
  };

  // T114: Handle preset button click
  const handlePresetClick = (preset: PresetType) => {
    setActivePreset(preset);

    if (preset === 'custom') {
      setShowCustomOptions(true);
      return; // Don't auto-apply settings for custom
    }

    setShowCustomOptions(false);
    const presetConfig = RECURRENCE_PRESETS[preset];
    setFrequency(presetConfig.frequency);
    setInterval(presetConfig.interval);

    // Reset weekdays for non-weekly presets
    if (presetConfig.frequency === 'WEEKLY') {
      setSelectedWeekdays([0]); // Default to Monday
    }

    if (enabled) {
      const newRule = createRRuleString({
        frequency: presetConfig.frequency,
        interval: presetConfig.interval,
        byweekday: presetConfig.frequency === 'WEEKLY' ? [0] : undefined,
      });

      onChange({
        enabled: true,
        rule: newRule,
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: getRecurrenceDescription(newRule),
      });
    }
  };

  // Handle frequency change
  const handleFrequencyChange = (newFrequency: 'DAILY' | 'WEEKLY' | 'MONTHLY') => {
    setFrequency(newFrequency);

    // Reset weekdays if changing to/from weekly
    if (newFrequency === 'WEEKLY' && selectedWeekdays.length === 0) {
      setSelectedWeekdays([0]); // Default to Monday
    }

    if (enabled) {
      const newRule = createRRuleString({
        frequency: newFrequency,
        interval,
        byweekday: newFrequency === 'WEEKLY' ? selectedWeekdays : undefined,
      });

      onChange({
        enabled: true,
        rule: newRule,
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: getRecurrenceDescription(newRule),
      });
    }
  };

  // Handle interval change
  const handleIntervalChange = (newInterval: number) => {
    if (newInterval < 1 || newInterval > 100) return; // Validate range

    setInterval(newInterval);

    if (enabled) {
      const newRule = createRRuleString({
        frequency,
        interval: newInterval,
        byweekday: frequency === 'WEEKLY' ? selectedWeekdays : undefined,
      });

      onChange({
        enabled: true,
        rule: newRule,
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: getRecurrenceDescription(newRule),
      });
    }
  };

  // Handle weekday toggle (T110)
  const handleWeekdayToggle = (weekdayIndex: number) => {
    const newWeekdays = selectedWeekdays.includes(weekdayIndex)
      ? selectedWeekdays.filter(d => d !== weekdayIndex)
      : [...selectedWeekdays, weekdayIndex].sort();

    // Ensure at least one weekday is selected
    if (newWeekdays.length === 0) return;

    setSelectedWeekdays(newWeekdays);

    if (enabled && frequency === 'WEEKLY') {
      const newRule = createRRuleString({
        frequency,
        interval,
        byweekday: newWeekdays,
      });

      onChange({
        enabled: true,
        rule: newRule,
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: getRecurrenceDescription(newRule),
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Enable/Disable Toggle */}
      <div className="flex items-center justify-between">
        <label htmlFor="recurrence-enabled" className="text-sm font-medium text-gray-900 dark:text-gray-100">
          Enable Recurrence
        </label>
        <input
          id="recurrence-enabled"
          type="checkbox"
          checked={enabled}
          onChange={(e) => handleToggle(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {enabled && (
        <>
          {/* T114: Preset Buttons for Quick Setup */}
          <div className="space-y-2">
            <label className="text-sm font-medium block text-gray-900 dark:text-gray-100">Quick Presets</label>
            <div className="grid grid-cols-4 gap-2">
              {(Object.entries(RECURRENCE_PRESETS) as [PresetType, typeof RECURRENCE_PRESETS[PresetType]][]).map(([key, preset]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => handlePresetClick(key)}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    activePreset === key
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
                  aria-pressed={activePreset === key}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          {/* Show custom options when Custom preset is selected or showCustomOptions is true */}
          {(activePreset === 'custom' || showCustomOptions) && (
            <>
              {/* Frequency Selector */}
              <div className="space-y-2">
                <label htmlFor="recurrence-frequency" className="text-sm font-medium block text-gray-900 dark:text-gray-100">
                  Frequency
                </label>
                <select
                  id="recurrence-frequency"
                  value={frequency}
                  onChange={(e) => handleFrequencyChange(e.target.value as 'DAILY' | 'WEEKLY' | 'MONTHLY')}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
                >
                  <option value="DAILY">Daily</option>
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                </select>
              </div>

              {/* Interval Input */}
              <div className="space-y-2">
                <label htmlFor="recurrence-interval" className="text-sm font-medium block text-gray-900 dark:text-gray-100">
                  Every
                </label>
                <div className="flex items-center gap-2">
                  <input
                    id="recurrence-interval"
                    type="number"
                    min="1"
                    max="100"
                    value={interval}
                    onChange={(e) => handleIntervalChange(parseInt(e.target.value, 10))}
                    className="w-20 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {frequency === 'DAILY' && (interval === 1 ? 'day' : 'days')}
                    {frequency === 'WEEKLY' && (interval === 1 ? 'week' : 'weeks')}
                    {frequency === 'MONTHLY' && (interval === 1 ? 'month' : 'months')}
                  </span>
                </div>
              </div>

              {/* Weekday Picker for Weekly Recurrence (T110) */}
              {frequency === 'WEEKLY' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium block text-gray-900 dark:text-gray-100">Repeat on</label>
                  <div className="grid grid-cols-7 gap-2">
                    {WEEKDAY_NAMES.map((day, index) => (
                      <button
                        key={day}
                        type="button"
                        onClick={() => handleWeekdayToggle(index)}
                        className={`rounded-md px-2 py-2 text-xs font-medium transition-colors ${
                          selectedWeekdays.includes(index)
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                        }`}
                        aria-pressed={selectedWeekdays.includes(index)}
                      >
                        {day.slice(0, 2)}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Human-Readable Description (FR-073) - Always visible when enabled */}
          <div className="rounded-md bg-gray-50 dark:bg-gray-800 p-3">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <span className="font-medium">Repeats:</span> {humanReadable}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
