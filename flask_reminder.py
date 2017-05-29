import flask
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


@app.route('/send_emails', methods=['GET','POST'])
def send_emails():
    """
    This function will receive an ajax request from the server containing the data of who should be emailed.
    Parse that data
    send email to fosters in that data.
    return json object containing successful message if successful, failure message if not.
    """
    """
    I think the_dictionary =
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
    """
    #get the credentials
    incoming_data = request.args.to_dict()
    print("Printing incoming data: ", incoming_data[''])
    the_dictionary = ast.literal_eval(incoming_data[''])
    # print("THE DICTIONARY:", the_dictionary)

    # in reality we'll want the return object to be a packet that contains the same data, and additional information
    # about the emails. for example, it would be great to know if any failed or anything you can find out about emails.
    # I dunno.


    credentials = valid_credentials()
    if not credentials:
        return None
    # create a service object for the user's email
    gmail_service = get_gmail_service(credentials)
    print("got service object")
    #get self - need to send all from the user that granted permission
    sender_name = gmail_service.users().getProfile(userId="me").execute()['emailAddress']
    check_marked = ast.literal_eval(list(request.args.to_dict().keys())[0])
    print ("got this: {}\ntype is: {}, yay".format(check_marked, str(type(check_marked))))

    # Results is a dictionary marking if emails were successfully sent - if an error occurred, mark false
    text_reminder = "Hello {},\n Make sure to give {} to {} today:\n{}\nThank you,\nGreen Hill Humane Society".format("Brian", "Hugs", "Little Grey", "Yayyayy!")
    msg = create_message(sender_name, "jamiez@uoregon.edu", "Daily Medicine Reminder", text_reminder)
    # send out the email!
    telegram(gmail_service, sender_name, msg)
    """
    results = dict()
    for entry in check_marked:
        text_reminder = "Hello {},\n Make sure to give {} to {} today:\n{}\nThank you,\nGreen Hill Humane Society".format(entry['Foster Name'], entry['Medication(s)'], entry['Animal Name(s)'], entry['Notes'])
        msg = create_message(sender_name, entry['Foster Email'], "Daily Medicine Reminder", text_reminder)
        # send out the email!
        telegram(gmail_service, sender_name, msg)
        results[entry['Foster Name']] = True;
    return jsonify(results)
    """
    return jsonify("Something indicating success.")

def telegram(service, userID, message):
    try:
        message = (service.users().messages().send(userId=userID, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except ():
        print('An error occurred: %s' % 'error')
    

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
