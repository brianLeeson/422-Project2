"""
Author(s): Brian Leeson

this is where the flask server will be implemented.
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
	if 'schedule' not in flask.session:
		app.logger.debug("Processing raw schedule file")
		raw = open(CONFIG.schedule)
		flask.session['schedule'] = pre.process(raw)
		raw.close()

	return flask.render_template('syllabus.html')