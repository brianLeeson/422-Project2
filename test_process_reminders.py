"""
Author(s): Brian Leeson

test file for nose tests to test the process_reminder functions
"""
import process_reminders as process


def test_create_reminders():
    """
    tests create_reminders function
    raises assertion error for failed test.
    """

    # real data from GH. Normal test, single line Notes field.
    event = {'etag': '"2989976944900000"', 'start': {'dateTime': '2017-05-18T10:30:00-07:00'}, 'htmlLink': 'https://www.google.com/calendar/event?eid=dGM1aTdicWk1cWg5NThya2ZicWdkb29xY2cgZ3JlZW4taGlsbC5vcmdfbzQwdTJxb2ZjOXYyZDI3M2dkdDRlaWhhdXNAZw', 'reminders': {'useDefault': True}, 'kind': 'calendar#event', 'end': {'dateTime': '2017-05-18T10:30:00-07:00'}, 'created': '2017-05-06T16:41:35.000Z', 'description': 'Foster Name: Katie Strick\nFoster Email: XXXX@email.com\nAnimal Name(s): Kitten\nMedication(s): Strongid\nNotes: Give by mouth.', 'organizer': {'displayName': 'Reminders - Kristi & Samantha', 'self': True, 'email': 'green-hill.org_o40u2qofc9v2d273gdt4eihaus@group.calendar.google.com'}, 'id': 'tc5i7bqi5qh958rkfbqgdooqcg', 'sequence': 0, 'hangoutLink': 'https://plus.google.com/hangouts/_/green-hill.org/katie-strick?hceid=Z3JlZW4taGlsbC5vcmdfbzQwdTJxb2ZjOXYyZDI3M2dkdDRlaWhhdXNAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ.tc5i7bqi5qh958rkfbqgdooqcg', 'updated': '2017-05-17T02:34:32.450Z', 'summary': 'Katie Strick- Reminder Strongid Due', 'status': 'confirmed', 'iCalUID': 'tc5i7bqi5qh958rkfbqgdooqcg@google.com', 'creator': {'email': 'samantha.ma@green-hill.org'}}

    result = process.create_reminders(event)
    expected = {
        "Foster Name": "Katie Strick",
        "Foster Email": "XXXX@email.com",
        "Animal Name(s)": "Kitten",
        "Medication(s)": "Strongid",
        "Notes": "Give by mouth."
    }

    print("result is", result)
    print("expected is", expected)
    assert result == expected

    # contrived data. Normal test. double line Notes field
    event = {'kind': 'calendar#event', 'end': {'timeZone': 'America/Los_Angeles', 'dateTime': '2017-05-19T13:00:00-07:00'}, 'status': 'confirmed', 'iCalUID': '60q6apb464p3ib9h6csj6b9k61ij8b9p71i3ab9g6oojac9p6tj62c9k6c@google.com', 'summary': 'Math group', 'created': '2017-05-16T19:59:38.000Z', 'description': "Foster Name: John Smith\nFoster Email: jsmith@email.com\nAnimal Name(s): Fluffy Bunny\nMedication(s): Love, Hugs\nNotes: Please give a large dose twice a day until condition improves.\nOh, and don't forget to email us back!", 'creator': {'displayName': 'Brian Leeson', 'email': 'cyberjunkie09@gmail.com', 'self': True}, 'start': {'timeZone': 'America/Los_Angeles', 'dateTime': '2017-05-19T11:00:00-07:00'}, 'sequence': 0, 'updated': '2017-05-18T20:55:07.563Z', 'reminders': {'overrides': [{'minutes': 30, 'method': 'popup'}], 'useDefault': False}, 'id': '60q6apb464p3ib9h6csj6b9k61ij8b9p71i3ab9g6oojac9p6tj62c9k6c', 'htmlLink': 'https://www.google.com/calendar/event?eid=NjBxNmFwYjQ2NHAzaWI5aDZjc2o2YjlrNjFpajhiOXA3MWkzYWI5ZzZvb2phYzlwNnRqNjJjOWs2YyBjeWJlcmp1bmtpZTA5QG0', 'organizer': {'displayName': 'Brian Leeson', 'email': 'cyberjunkie09@gmail.com', 'self': True}, 'etag': '"2990105685653000"'}

    result = process.create_reminders(event)
    expected = {
        "Foster Name": "John Smith",
        "Foster Email": "jsmith@email.com",
        "Animal Name(s)": "Fluffy Bunny",
        "Medication(s)": "Love, Hugs",
        "Notes": "Please give a large dose twice a day until condition improves. Oh, and don't forget to email us back!"
    }
    print("result is", result)
    print("expected is", expected)
    assert result == expected
