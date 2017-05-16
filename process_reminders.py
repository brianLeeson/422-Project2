"""
Author(s): Brian Leeson

Calendar parsing functions should go here.
"""


def create_reminders(event):
    """
    (str) -> Reminder
    takes a google calender event and returns a dictionary with of the field values if the standard format is followed.
    if description field does not match the correct format, None is returned.
    
    Standard format:
    
    Foster Name: John Smith
    Foster Email: jsmith@email.com
    Animal Name(s): Fluffy Bunny
    Medication(s): Love, Hugs
    Notes: Please give a large dose twice a day until condition improves.
    Oh, and don't forget to email us back!
    
    Dictionary looks like
    dict = {
        Foster Name : "John Smith",
        Foster Email : "jsmith@email.com",
        Animal Name(s) : "Fluffy Bunny",
        Medication(s) : "Love, Hugs",
        Notes : "Please give a large dose twice a day until condition improves. Oh, and don't forget to email us back!"
    }

    """
    reminder = {}
    NUM_FIELDS = 5
    des = event['description']
    lines = des.split('\n')

    if len(lines) < NUM_FIELDS:
        return None

    # store key : value in dict
    ctr = 0
    while ctr < NUM_FIELDS:
        firstCol = lines[ctr].find(':')
        if firstCol == -1:
            return None
        key = lines[ctr][:firstCol].strip()
        value = lines[ctr][firstCol + 1:].strip()
        reminder[key] = value
        ctr += 1

    # notes could be more than one line. handling
    leftOver = ''
    for i in range(ctr, len(lines)):
        leftOver += lines[i]
    reminder["Notes"] += " " + leftOver

    return reminder
