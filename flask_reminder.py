import flask
import json
import urllib.request
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify
import uuid

import json
import logging

# Date handling 
import arrow  # Replacement for datetime, based on moment.js

# OAuth2  - Google library implementation for convenience
from oauth2client import client
import httplib2  # used in oauth2 flow

# Google API for services 
from apiclient import discovery

import sys
sys.path.insert(0, "./secrets/")
import CONFIG
import admin_secrets  # Per-machine secrets

import process_reminders as process


# Globals
app = flask.Flask(__name__)
app.debug = CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
app.secret_key = CONFIG.secret_key

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = admin_secrets.google_key_file

# ID of the calendar that stores all of the event reminders.
REMINDER_ID = "green-hill.org_o40u2qofc9v2d273gdt4eihaus@group.calendar.google.com"

# Pages (routed from URLs)


@app.route("/")
@app.route("/index")
def index():
    """
    Renders homepage. 
    I don't believe we need to initialize any state on the server
    """
    app.logger.debug("Entering index")
    return render_template('index.html')


@app.route('/authenticate')
def authenticate():
    """
    This function checks if the server has valid credentials \
    and if not asks for them: flask.redirect(flask.url_for('oauth2callback')) 
    Now that we are sure to have creds, get a gcal_service object.
    Then list the calendars using the service object.
    """
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:  # not None is True. weird.
        app.logger.debug("Redirecting to authorization")
        return flask.redirect(flask.url_for('oauth2callback'))

    return render_template('success.html')


@app.route('/generate')
def generate():
    """
    This function gets all reminder event for today and returns them as a json object
    This function assumes that valid credentials have already been obtained.
    """
    app.logger.debug("Generating reminders")
    credentials = valid_credentials()
    if not credentials:
        return None

    gcal_service = get_gcal_service(credentials)

    allReminders = generateReminders(gcal_service)
    """
    allReminders should look like
    allReminders = {  
        0 : {
        Foster Name : "John Smith",
        Foster Email : "jsmith@email.com",
        Animal Name(s) : "Fluffy Bunny",
        Medication(s) : "Love, Hugs",
        Notes : "Please give a large dose twice a day until condition improves. Oh, and don't forget to email us back!"
        }
        1 : {
        Foster Name : "blah",
        Foster Email : "blah",
        Animal Name(s) : "blah",
        Medication(s) : "blah",
        Notes : "blah"
        }
        ...and so on
    }
    """

    return jsonify(allReminders)

@app.route('/fakedata', methods=['GET','POST'])
def fakedata():
    """ Fake data for Amie to work with correctly formatted JSON objects..."""
    animal_dict = {0: {"Foster Name": "John Smith", "Foster Email": "jsmith@email.com",
                       "Animal Name(s)": "Fluffy Bunny", "Medication(s)": "Love, Hugs",
                        "Notes": "blah blah blah blah"},
                   1: {"Foster Name": "Brian Leeson", "Foster Email": "bleeson@email.com",
                       "Animal Name(s)": "Oreo", "Medication(s)": "Milk",
                        "Notes": "meow meow meow meow meow"},
                   2: {"Foster Name": "Amie Corso", "Foster Email":"acorso@uoregon.edu",
                       "Animal Name(s)": "Fatface, Marmot", "Medication(s)": "Diet Pills",
                       "Notes": "Get one of those little cat leashes and walk these thugs"}
                   }
    return jsonify(animal_dict)

@app.route('/testsendemails', methods=['GET','POST'])
def testsendemails():
    """ temporary route to explore form submission"""
    #incoming_data = jsonify(request.get_json())
    #incoming_data = request.args.get("thedata", type=str)
    #str_response = response.readall().decode('utf-8')
    #incoming_data = urllib.request.unquote(request.query_string)
    incoming_data = request.args.to_dict()
    print("Printing incoming data: ", incoming_data)

    return jsonify("Something indicating success.")


@app.route('/send_emails')
def send_emails():
    """
    This function will receive an ajax request from the server containing the data of who should be emailed.
    Parse that data
    send email to fosters in that data.
    return json object containing successful message if successful, failure message if not.
    """
    """
    data will come from the client looking like this:
    allReminders = {  
        0 : {
        Foster Name : "John Smith",
        Foster Email : "jsmith@email.com",
        Animal Name(s) : "Fluffy Bunny",
        Medication(s) : "Love, Hugs",
        Notes : "Please give a large dose twice a day until condition improves. Oh, and don't forget to email us back!"
        }
        1 : {
        Foster Name : "blah",
        Foster Email : "blah",
        Animal Name(s) : "blah",
        Medication(s) : "blah",
        Notes : "blah"
        }
        and so on
    }
    """

    return jsonify("Something signifying success.")

####
#
#  Google calendar authorization:
#      Returns us to the main /choose screen after inserting
#      the calendar_service object in the session state.  May
#      redirect to OAuth server first, and may take multiple
#      trips through the oauth2 callback function.
#
#  Protocol for use ON EACH REQUEST: 
#     First, check for valid credentials
#     If we don't have valid credentials
#         Get credentials (jump to the oauth2 protocol)
#         (redirects back to /choose, this time with credentials)
#     If we do have valid credentials
#         Get the service object
#
#  The final result of successful authorization is a 'service'
#  object.  We use a 'service' object to actually retrieve data
#  from the Google services. Service objects are NOT serializable ---
#  we can't stash one in a cookie.  Instead, on each request we
#  get a fresh service object from our credentials, which are
#  serializable. 
#
#  Note that after authorization we always redirect to /choose;
#  If this is unsatisfactory, we'll need a session variable to use
#  as a 'continuation' or 'return address' to use instead. 
#
####


def valid_credentials():
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value. 
    """
    if 'credentials' not in flask.session:
        return None

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if (credentials.invalid or credentials.access_token_expired):
        return None
    return credentials


def get_gcal_service(credentials):
    """
    We need a Google calendar 'service' object to obtain
    list of calendars, busy times, etc.  This requires
    authorization. If authorization is already in effect,
    we'll just return with the authorization. Otherwise,
    control flow will be interrupted by authorization, and we'll
    end up redirected back to /choose *without a service object*.
    Then the second call will succeed without additional authorization.
    """
    app.logger.debug("Entering get_gcal_service")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http_auth)
    app.logger.debug("Returning service")
    return service


@app.route('/oauth2callback')
def oauth2callback():
    """
    The 'flow' has this one place to call back to.  We'll enter here
    more than once as steps in the flow are completed, and need to keep
    track of how far we've gotten. The first time we do the first
    step, the second time we'll skip the first step and do the second,
    and so on.
    """
    app.logger.debug("Entering oauth2callback")
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope=SCOPES,
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    # Note we are *not* redirecting above.  We are noting *where*
    # we will redirect to, which is this function.

    # The *second* time we enter here, it's a callback
    # with 'code' set in the URL parameter.  If we don't
    # see that, it must be the first time through, so we
    # need to do step 1.
    app.logger.debug("Got flow")
    if 'code' not in flask.request.args:
        app.logger.debug("Code not in flask.request.args")
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    # This will redirect back here, but the second time through
    # we'll have the 'code' parameter set
    else:
        # It's the second time through ... we can tell because
        # we got the 'code' argument in the URL.
        app.logger.debug("Code was in flask.request.args")
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        # Now I can build the service and execute the query,
        # but for the moment I'll just log it and go back to
        # the main screen
        app.logger.debug("Got credentials")
        return flask.redirect(flask.url_for('authenticate'))


#  Functions (NOT pages) that return some information

def generateReminders(service):
    """
    This function parses reminder cal data
    returns a dict of reminder instances.
    """

    app.logger.debug("Entering generateReminders")
    # get all calendars on gmail account.
    calendar_list = service.calendarList().list().execute()["items"]  # TODO: understand this api request

    today = arrow.now('local')
    today = today.fromdate(today, tzinfo='local')
    tomorrow = today.replace(days=+1)  # up until but not including "tomorrow"

    timeMin = today.isoformat()
    timeMax = tomorrow.isoformat()

    reminderDict = {}
    for cal in calendar_list:
        if cal['id'] == REMINDER_ID:
            events = service.events().list(calendarId=cal['id'], timeMin=timeMin,
                                           timeMax=timeMax, singleEvents=True).execute()['items']
            eventNum = 0
            for event in events:
                if "description" in event:
                    # process event
                    value = process.create_reminders(event)
                    key = eventNum
                    reminderDict[key] = value
                    eventNum += 1

    return reminderDict


if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    # (e.g., if we are running under green unicorn)
    # print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
