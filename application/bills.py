#!/usr/bin/env python
from flask import g, render_template, url_for, redirect, abort
from datetime import datetime, date, timedelta
from collections import OrderedDict
import json
import inspect
import os
from application import app

def json_check(fn):
    """ Look to see if a JSON file exists. If it does, return it.
        If not, create the file and return an empty JSON-friendly string.

        We do this so an open() and json_load() will fail gracefully without
        a whole bunch of try / except clauses.
        """
    if not os.path.isfile(fn):
        fh = open(fn, 'wb')
        json.dump('{ "items": [] }', fh)
        fh.close()
    fh = open(fn)
    return fh

@app.route('/')
def index():
    app.page['title'] = 'Bill Tracker'
    app.page['description'] = 'Tracking legislation in Colorado\'s state house.'
    response = {
        'app': app,
    }
    return render_template('home.html', response=response)

@app.route('/bills/')
def session_index():
    app.page['title'] = 'Sessions'
    app.page['description'] = 'An index of Colorado legislative sessions we have bills for.'
    response = {
        'app': app,
    }
    return render_template('session_index.html', response=response)

@app.route('/bills/<session>/')
def session_detail():
    app.page['title'] = ''
    app.page['description'] = ''
    response = {
        'app': app,
    }
    return render_template('session_detail.html', response=response)
