import requests
from icalendar import Calendar

FEEDS = {

}

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

with open("merged.ics", "wb") as f:
    f.write(merged_calendar.to_ical())

print(
    f"Klaar! {len(merged_events)} unieke lessen "
    "geschreven naar gezamenlijke.ics"
)
