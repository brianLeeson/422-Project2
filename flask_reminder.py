import flask
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


# Globals
app = flask.Flask(__name__)
app.debug = CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
app.secret_key = CONFIG.secret_key

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = admin_secrets.google_key_file
APPLICATION_NAME = 'MeetMe class project'

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


@app.route('/generate')
def generate():
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

    gcal_service = get_gcal_service(credentials)
    app.logger.debug("Returned from get_gcal_service")

    # NOTE: looks like parsed data from l_c will be saved in session(?) and not sent as json in response to ajax
    # do we want to keep or have sending the parsed data not happen right after we get auth.
    # probably should do right after auth.

    # NOTE: below is a way for you to save data in the session(?) variable.
    # flask.g.calendars = list_calendars(gcal_service)

    list_calendars(gcal_service)

    return render_template('success.html')

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
        return flask.redirect(flask.url_for('generate'))


#  Functions (NOT pages) that return some information


def list_calendars(service):
    """
    currently set up to log a users calendar for the week. This is were parsing of calendar data will happen.
    returns None
    
    potential pseudo code:
    get cals
    key into reminder cal
    ask for all events for today.
    parse those events.
    package to send to amie
    then what??
    
    """

    app.logger.debug("Entering list_calendars")
    # get all calendars on gmail account.
    calendar_list = service.calendarList().list().execute()["items"]  # TODO: understand this api request

    f = open('server_log.txt', 'a')
    f.write("\n ------- SOMEONE CLICKED THE BUTTON. CAL LIST:\n")

    today = arrow.now('local')
    today = today.fromdate(today, tzinfo='local')

    print("TODAY IS:", today)
    tomorrow = today.replace(days=+1)  # TODO 'oneWeek' replace after GH log
    oneWeek = today.replace(days=+7)
    timeMin = today.isoformat()
    timeMax = oneWeek.isoformat()

    for cal in calendar_list:
        # write all calendar to log. we will use the cal id to get info
        f.write("\nCAL IS:\n")
        f.write(cal.__str__() + "\n")

        events = service.events().list(calendarId=cal['id'], timeMin=timeMin,
                                       timeMax=timeMax, singleEvents=True).execute()['items']

        # write all of the calendars events to logs
        f.write("\n-----EVENTS ARE: \n")
        for event in events:
            f.write("\n---EVENT: \n")
            f.write(event.__str__() + "\n")

    f.close()
    return None


if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    # (e.g., if we are running under green unicorn)
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
