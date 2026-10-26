import requests
from icalendar import Calendar
import os
import uuid
from datetime import datetime, time

#secrets

FEEDS = {
    "thijs": os.environ["THIJS"].strip(),
    "lucas": os.environ["LUCAS"].strip(),
    "marnix": os.environ["MARNIX"].strip(),
    "niels": os.environ["NIELS"].strip(),
    "thijs R.": os.environ["THIJSR"].strip(),
    "bjorn": os.environ["BJORN"].strip(),
    "quinten": os.environ["QUINTEN"].strip(),
    "aaron": os.environ["AARON"].strip()
}

student_events = {name: [] for name in FEEDS}

LESSON_TIMES = [
    ("08:30", "09:20"),
    ("09:20", "10:10"),
    ("10:30", "11:20"),
    ("11:20", "12:10"),
    ("12:40", "13:30"),
    ("13:30", "14:20"),
    ("14:30", "15:20"),
    ("15:20", "16:10"),
    ("16:10", "17:00"),
]

print(FEEDS)

merged_events = {}

for student_name, url in FEEDS.items():
    print(f"Downloaden: {student_name}")

    data = requests.get(url).text
    cal = Calendar.from_ical(data)

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        start = component.get("DTSTART").dt
        end = component.get("DTEND").dt
        student_events[student_name].append((start, end))

        summary = str(component.get("SUMMARY", ""))
        location = str(component.get("LOCATION", ""))

        # Unieke sleutel
        key = (
            start,
            end,
            summary,
            location
        )

        if key not in merged_events:
            merged_events[key] = {
                "event": component,
                "students": [student_name]
            }
        else:
            merged_events[key]["students"].append(student_name)

# Nieuwe kalender maken
merged_calendar = Calendar()
merged_calendar.add("prodid", "-//Gezamenlijk Rooster//")
merged_calendar.add("version", "2.0")

for info in merged_events.values():
    event = info["event"]

    students = sorted(info["students"])

    original_summary = str(event.get("SUMMARY", ""))

    # Titel blijft netjes
    event["SUMMARY"] = original_summary

    # Beschrijving uitbreiden
    old_description = str(event.get("DESCRIPTION", ""))

    new_description = (
        old_description
        + "\n\nAanwezig:\n"
        + "\n".join(students)
    )

    event["DESCRIPTION"] = new_description

    merged_calendar.add_component(event)

dates = {
    start.date()
    for lessons in student_events.values()
    for start, end in lessons
    if isinstance(start, datetime)
}

for date in dates:
    for start_str, end_str in LESSON_TIMES:
        start_time = time.fromisoformat(start_str)
        end_time = time.fromisoformat(end_str)

        start = datetime.combine(date, start_time)
        end = datetime.combine(date, end_time)

        # Find students with a lesson during this period
        busy_students = set()

        for student, lessons in student_events.items():
            for lesson_start, lesson_end in lessons:
                if lesson_start < end and lesson_end > start:
                    busy_students.add(student)
                    break

        free_students = sorted(
            set(FEEDS.keys()) - busy_students
        )

        if not free_students:
            continue

        free_event = Event()
        free_event.add("uid", f"{uuid.uuid4()}@rooster")
        free_event.add("dtstamp", datetime.now().astimezone())
        free_event.add("dtstart", start)
        free_event.add("dtend", end)
        free_event.add(
            "summary",
            "Vrij: " + ", ".join(free_students)
        )
        free_event.add(
            "description",
            "Studenten zonder les:\n" + "\n".join(free_students)
        )

        merged_calendar.add_component(free_event)

with open("merged.ics", "wb") as f:
    f.write(merged_calendar.to_ical())

print(
    f"Klaar! {len(merged_events)} unieke lessen "
    "geschreven naar merged.ics"
)