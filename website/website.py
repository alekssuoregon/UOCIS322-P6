import flask
from flask import request
import config
import requests
import json
import os

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

#docker-compose environment variables
API_ADDR = os.environ['BACKEND_ADDR']
API_PORT = os.environ['BACKEND_PORT']

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('index.html')


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############


#Simply performs a few different types of API data GETs to display on the page
@app.route("/_get_api_data")
def _calc_times():
    r = requests.get("http://"+API_ADDR+":"+API_PORT+"/listAll?top=3")
    all_text = r.text

    r = requests.get("http://"+API_ADDR+":"+API_PORT+"/listOpenOnly/csv?top=3")
    open_text = r.text

    r = requests.get("http://"+API_ADDR+":"+API_PORT+"/listCloseOnly/csv?top=3")
    close_text = r.text

    return flask.jsonify({"all": all_text, "open": open_text, "close": close_text})


app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
