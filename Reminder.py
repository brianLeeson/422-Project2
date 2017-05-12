"""
Author(s): Brian Leeson
This Class is for storing the reminder event information

the information in this class comes from a form that looks like this:
Foster Name: John Smith
Foster Email: jsmith@email.com
Animal Name(s): Fluffy Bunny
Medication(s): Love, Hugs
Notes: Please give a large dose twice a day until condition improves.
"""


class Reminder:
    """ 
    This class will represent an individuals survey results
    """

    def __init__(self, fName, fEmail, aName, med, notes):
        self._fName = fName
        self._fEmail = fEmail
        self._aName = aName
        self._med = med
        self._notes = notes

    def __str__(self):
        return self._fEmail + " " + self._med


