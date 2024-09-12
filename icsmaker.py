#!/usr/bin/env python3

import argparse
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import sys

# Timezone setup
tz = pytz.timezone('Europe/Zagreb')

# Fixed time slots for the events (index-based)
time_slots = {
    1: {'start': (8, 0), 'end': (8, 45)},
    2: {'start': (8, 50), 'end': (9, 35)},
    3: {'start': (9, 40), 'end': (10, 25)},
    4: {'start': (10, 40), 'end': (11, 25)},
    5: {'start': (11, 30), 'end': (12, 15)},
    6: {'start': (12, 20), 'end': (13, 5)},
    7: {'start': (13, 10), 'end': (13, 55)}
}

# Read events from a file
def read_events_from_file(filename):
    events = []
    with open(filename, 'r') as file:
        for line in file:
            # Expected format: "Day, Event Name, Time Slot Index"
            line = line.strip()
            if line:
                parts = line.split(',')
                if len(parts) != 3:
                    print(f"Skipping invalid line: {line}")
                    continue

                day, name, slot_index = parts
                try:
                    slot_index = int(slot_index.strip())
                    if slot_index not in time_slots:
                        print(f"Invalid time slot index '{slot_index}' in file. Skipping line: {line}")
                        continue
                except ValueError:
                    print(f"Invalid time slot index '{slot_index}' in file. Skipping line: {line}")
                    continue

                events.append({
                    'day': day.strip().upper(),
                    'name': name.strip(),
                    'slot_index': slot_index
                })
    return events

# Create calendar
def create_calendar(events):
    calendar = Calendar()
    calendar.add('prodid', '-//Your Organization//NONSGML v1.0//EN')
    calendar.add('version', '2.0')
    start_date = datetime(2024, 9, 9)  # The first Monday of the schedule

    day_offsets = {
        'MO': 0,  # Monday
        'TU': 1,  # Tuesday
        'WE': 2,  # Wednesday
        'TH': 3,  # Thursday
        'FR': 4   # Friday
    }

    for event_info in events:
        day = event_info['day']
        if day not in day_offsets:
            print(f"Invalid day '{day}' in events file. Skipping.")
            continue

        day_offset = day_offsets[day]
        slot_index = event_info['slot_index']

        # Get start and end time from the time slots dictionary
        start_hour, start_minute = time_slots[slot_index]['start']
        end_hour, end_minute = time_slots[slot_index]['end']

        event_start = tz.localize(datetime(2024, 9, 9 + day_offset, start_hour, start_minute))
        event_end = tz.localize(datetime(2024, 9, 9 + day_offset, end_hour, end_minute))

        event = Event()
        event.add('summary', event_info['name'])
        event.add('dtstart', event_start)
        event.add('dtend', event_end)
        event.add('location', "Room 101")
        event.add('description', "Replace this with the actual event details")
        event.add('uid', f"{event_start.strftime('%Y%m%dT%H%M%S')}-dummy@yourdomain.com")

        # Set recurrence rule for every two weeks
        event.add('rrule', {'freq': 'weekly', 'interval': 2, 'byday': day})

        calendar.add_component(event)

    return calendar

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Generate an ICS file from event details.')
    parser.add_argument('events_file', help='Path to the events file')
    parser.add_argument('-o', '--output', help='Name of the output ICS file (if not provided, write to stdout)')

    # Parse the arguments
    args = parser.parse_args()

    # Read events from the provided input file
    events = read_events_from_file(args.events_file)

    # Create the calendar with the events
    calendar = create_calendar(events)

    # Write calendar to output file or stdout
    if args.output:
        with open(args.output, 'wb') as file:
            file.write(calendar.to_ical())
        print(f"ICS file '{args.output}' created successfully.")
    else:
        sys.stdout.buffer.write(calendar.to_ical())

if __name__ == '__main__':
    main()
