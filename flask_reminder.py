import flask
import json
from flask import render_template
from flask import request
from flask import jsonify
import logging

import ast

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

# Email Object type & encoding mechanism
from email.mime.text import MIMEText
import base64
import ast

# Globals
app = flask.Flask(__name__)
app.debug = CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
app.secret_key = CONFIG.secret_key

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly https://mail.google.com/'
CLIENT_SECRET_FILE = admin_secrets.google_key_file

# ID of the calendar that stores all of the event reminders.
REMINDER_ID = "green-hill.org_o40u2qofc9v2d273gdt4eihaus@group.calendar.google.com"

TESTING_EMAIL = True  # if True, emails only get sent to TEST_EMAIL
TEST_EMAIL = "brianeleeson@gmail.com, cyberjunkie09@gmail.com"

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


@app.route('/send_emails', methods=['GET', 'POST'])
def send_emails():
    """
    This function will receive an ajax request from the server containing the data of who should be emailed.
    Parse that data
    send email to fosters in that data.
    return json dictionary mimicking the input data.
        'reminders_to_email' field contains the emails that WERE sent. 
        'unselected_reminders' are emails that the user didn't select and still need to be displayed
        'failed_send' are emails that were selected and attempted to send, but an error occurred.

    INPUT->
    the_dictionary =
    {"reminders_to_email":
            {"0":
                {"Animal Name(s)":"Fluffy Bunny",
                "Foster Email":"jsmith@email.com",
                "Foster Name":"John Smith",
                "Medication(s)":"Love, Hugs",
                "Notes":"Please give a large dose twice a day until condition improves. Oh, and don\'t forget to email us back!"}
            },
            "unselected_reminders":{}
    }

    OUTPUT->
    the_dictionary =
    {"unselected_reminders":
            {"0":
                {"Animal Name(s)":"Fluffy Bunny",
                "Foster Email":"jsmith@email.com",
                "Foster Name":"John Smith",
                "Medication(s)":"Love, Hugs",
                "Notes":"Please give a large dose twice a day until condition improves. Oh, and don\'t forget to email us back!"}
            },
    "reminders_to_email":
            {"0":
                {"Animal Name(s)":"Bug",
                "Foster Email":"yellow@yellow.com",
                "Foster Name":"Amie Jamie",
                "Medication(s)":"Long Walk",
                "Notes":"Only take her favorite yellow leash."}
            },},
    "failed_send":{}
    }
    """
    incoming_data = request.args.to_dict()
    the_dictionary = ast.literal_eval(incoming_data[''])

    credentials = valid_credentials()
    if not credentials:
        return None
    # create a service object for the user's email
    gmail_service = get_gmail_service(credentials)

    # get self - need to send all from the user that granted permission
    sender_name = gmail_service.users().getProfile(userId="me").execute()['emailAddress']

    emails_to_send = the_dictionary['reminders_to_email']  # only the emails we need to send

    # we don't know what the keys are (usually some stringified number, but they are unpredictable,
    # and not in ascending order or reliably starting at 0)
    the_keys = list(emails_to_send.keys())  # TODO getting list of keys not needed. can iterate over dict directly
    failed = []

    for entry in the_keys:  # entry is itself a dictionary, mapping a stringified number to an event reminder data
        reminder = emails_to_send[entry]

        foster_name = reminder['Foster Name']
        medications = reminder['Medication(s)']
        animal_name = reminder['Animal Name(s)']
        notes = reminder['Notes']
        email_string = "Hello {},\n\nMake sure to give {} to {} today.\nNotes: {}\n\nWhen you have given: " + medications +  \
                       ", or if you have any questions, please email use back.\nThank you,\nGreen Hill Humane Society"

        text_reminder = email_string.format(foster_name, medications, animal_name, notes)

        foster_email = reminder['Foster Email']
        email_subject = "Daily Medicine Reminder"

        if TESTING_EMAIL:
            foster_email = TEST_EMAIL

        msg = create_message(sender_name, foster_email, email_subject, text_reminder)

        # send out the email!
        sent = telegram(gmail_service, sender_name, msg)
        if not sent:
            failed.append(reminder)

    failures = {}
    for i in range(len(failed)):
        failures[str(i)] = failed[i]
    the_dictionary['failed_send'] = failures  # add a new field to the original dictionary of the emails that failed

    return json.dumps(the_dictionary)


def telegram(service, userID, message):
    try:
        message = (service.users().messages().send(userId=userID, body=message).execute())
        return message
    except ():
        return None


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

      Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')}


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


def get_gmail_service(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http_auth)
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


# Functions (NOT pages) that return some information

def generateReminders(service):
    """
    This function parses reminder cal data
    returns a dict of reminder instances.
    """

    app.logger.debug("Entering generateReminders")
    # get all calendars on gmail account.
    calendar_list = service.calendarList().list().execute()["items"]  # TODO: understand this api request. only query needed?

    today = arrow.now('local')
    today = today.fromdate(today, tzinfo='local')
    tomorrow = today.replace(days=+1)  # up until but not including "tomorrow"

    timeMin = today.isoformat()
    timeMax = tomorrow.isoformat()

    reminderDict = {}
    for cal in calendar_list:
        # if cal['id'] == REMINDER_ID: # commented out to look through all calendars.
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
