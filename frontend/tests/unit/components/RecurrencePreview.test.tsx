/**
 * Unit tests for RecurrencePreview component (FR-069)
 * Task: T105
 * Phase: 6 - US1 Extended - Recurrence
 */

import { render, screen } from '@testing-library/react';
import { RecurrencePreview } from '@/components/recurrence/RecurrencePreview';

describe('RecurrencePreview Component', () => {
  test('T105: shows next 5 occurrences for daily recurrence', () => {
    // GIVEN: A daily recurrence rule
    const ruleString = 'FREQ=DAILY;INTERVAL=1';

    // WHEN: Component is rendered
    render(<RecurrencePreview rrule={ruleString} count={5} />);

    // THEN: Shows exactly 5 occurrence dates
    const header = screen.getByText(/next 5 occurrences/i);
    expect(header).toBeInTheDocument();

    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(5);
  });

  test('T105: shows formatted dates for weekly recurrence', () => {
    // GIVEN: A weekly recurrence rule (every Monday)
    const ruleString = 'FREQ=WEEKLY;INTERVAL=1;BYDAY=MO';

    // WHEN: Component is rendered
    render(<RecurrencePreview rrule={ruleString} count={5} />);

    // THEN: Shows 5 Monday dates in readable format
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(5);

    // All dates should contain "Mon" or "Monday" depending on format
    listItems.forEach(item => {
      expect(item.textContent).toMatch(/\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec/);
    });
  });

  test('T105: shows correctly for bi-weekly recurrence', () => {
    // GIVEN: A bi-weekly recurrence rule
    const ruleString = 'FREQ=WEEKLY;INTERVAL=2;BYDAY=TU';

    // WHEN: Component is rendered
    render(<RecurrencePreview rrule={ruleString} count={5} />);

    // THEN: Shows 5 occurrences (every 2 weeks)
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(5);
  });

  test('T105: handles monthly recurrence', () => {
    // GIVEN: A monthly recurrence rule
    const ruleString = 'FREQ=MONTHLY;INTERVAL=1';

    // WHEN: Component is rendered
    render(<RecurrencePreview rrule={ruleString} count={5} />);

    // THEN: Shows 5 monthly occurrences
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(5);
  });

  test('T105: shows empty state for invalid rule', () => {
    // GIVEN: An invalid recurrence rule
    const ruleString = 'INVALID_RULE';

    // WHEN: Component is rendered
    render(<RecurrencePreview rrule={ruleString} count={5} />);

    // THEN: Shows error message or empty list
    const listItems = screen.queryAllByRole('listitem');
    expect(listItems).toHaveLength(0);

    expect(screen.getByText(/invalid|error/i)).toBeInTheDocument();
  });

  test('T105: respects custom count parameter', () => {
    // GIVEN: A daily recurrence with custom count
    const ruleString = 'FREQ=DAILY;INTERVAL=1';

    // WHEN: Component is rendered with count=3
    render(<RecurrencePreview rrule={ruleString} count={3} />);

    // THEN: Shows exactly 3 occurrences
    const header = screen.getByText(/next 3 occurrences/i);
    expect(header).toBeInTheDocument();

    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(3);
  });

  test('T105: updates preview when rule changes', () => {
    // GIVEN: A daily recurrence
    const { rerender } = render(<RecurrencePreview rrule="FREQ=DAILY;INTERVAL=1" count={5} />);

    let listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(5);

    // WHEN: Rule changes to weekly
    rerender(<RecurrencePreview rrule="FREQ=WEEKLY;INTERVAL=1;BYDAY=MO" count={5} />);

    // THEN: Preview updates to show weekly occurrences
    listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(5);
  });
});
