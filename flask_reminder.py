"""
Author(s): Brian Leeson

This is where the flask server will be implemented.

To run this test server:
"make run"
open browser
"localhost:8000" into url
be amazed
"""


import flask
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

# Date handling - likely need some of these for dealing with dates
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times


###
# Globals
###
app = flask.Flask(__name__)


@app.route("/")
@app.route("/index")
@app.route("/schedule")
def index():
	app.logger.debug("Main page entry")

	return flask.render_template('index.html')

# TODO: setup config script?
# app.secret_key = CONFIG.secret_key
# app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
if __name__ == "__main__":
	port = 8000  # TODO: arbitrary port num. could do better
	print("Opening for global access on port {}".format(port))
	app.run(port=port, host="0.0.0.0")
