import requests
from icalendar import Calendar

FEEDS = {
    "thijs": "https://api.somtoday.nl/rest/v1/icalendar/stream/0792a6e2-9833-45e8-b1eb-1498cf22f10d/02a633dc-b7b4-4a08-8371-45e60b8bc106",
    "niels": "https://api.somtoday.nl/rest/v1/icalendar/stream/0792a6e2-9833-45e8-b1eb-1498cf22f10d/5698efc6-18c2-4b53-b816-37c87e02a376",
    "lucas": "https://api.somtoday.nl/rest/v1/icalendar/stream/0792a6e2-9833-45e8-b1eb-1498cf22f10d/80e15401-bb1d-44ff-a501-b8fea2e37ccc",
    "marnix": "https://api.somtoday.nl/rest/v1/icalendar/stream/0792a6e2-9833-45e8-b1eb-1498cf22f10d/e13a6ac5-735c-4943-8765-d9b15bc102d0"
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