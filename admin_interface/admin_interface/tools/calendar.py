import icalendar
import recurring_ical_events
import urllib.request
import logging

from datetime import datetime, timedelta

cal_url = "https://calendar.google.com/calendar/ical/s6pg5kgtmu98ibee92h5d1gqh0%40group.calendar.google.com/public/basic.ics"  # From google

today = datetime.now()

ical_string = None
ical_string_age = datetime.now()


def getEvents():
    global ical_string

    now = datetime.now()
    # Check if we need to re-download cal
    if ical_string_age < now - timedelta(hours=5) or ical_string == None:
        logging.info("Downloading a new calendar string.")
        ical_string = urllib.request.urlopen(cal_url).read()

    # Extract info from cal
    calendar = icalendar.Calendar.from_ical(ical_string)
    events = recurring_ical_events.of(calendar).between(
        today, today + timedelta(days=15)
    )

    return events


def getNextEvent():
    # Get events
    events = getEvents()

    # Oldest first
    events.reverse()

    _ret = "No Upcoming Meetings."
    _days = 100

    for event in events:
        if "Meeting" in event["SUMMARY"]:
            duration = event["DTSTART"].dt.replace(
                tzinfo=None
            ) - datetime.now().replace(tzinfo=None)

            days = duration.days
            hours = int(duration.seconds / (60 * 60))
            minutes = int((duration.seconds - int(hours * (60 * 60))) / 60)

            logging.debug(f"Found {event['SUMMARY']} only {days} away.")

            # Make sure we're adding the closest meeting.
            if days < _days and days >= 0:
                _ret = f"Next meeting in {days} days, {hours} hours, {minutes} minutes."
                _days = days

    return _ret
