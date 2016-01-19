#!/usr/bin/env python
from flask import g, render_template, url_for, redirect, abort
from datetime import datetime, date, timedelta
from collections import OrderedDict
import json
import inspect
import os
from application import app

class BillQuery:
    """ A means of querying the list of bills.
        A bill record looks something like this:
        {
            "title": "Sentencing For Certain 2nd Degree Assaults",
            "created_at": "2015-03-24 21:28:11",
            "updated_at": "2015-10-07 12:07:47",
            "chamber": "lower",
            "state": "co",
            "session": "2015A",
            "subjects": [],
            "type": ["bill"],
            "id": "COB00003396",
            "bill_id": "HB 15-1303"
        }
        """

    def __init__(self):
        """
            """
        self.bills = json.load(json_check('_input/co-bills.json'))
        self.session = app.session.upper()

    def query_session(self, *session):
        """ Take a session, and, if valid, return the bills form that session.
            """
        # If we don't pass it a session it defaults to the current session.
        if not session:
            session = self.session
        filtered = []

        for item in self.bills:
            if item['session'] == self.session:
                filtered.append(item)
        return filtered

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
    q = BillQuery()
    response = {
        'app': app,
        'bills': q.query_session()
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
def session_detail(session):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Session: %s' % session
    app.page['description'] = ''
    data = {
        'bills': json.load(json_check('_input/co-bills.json'))
    }
    response = {
        'app': app,
        'session': session,
        'data': data
    }
    return render_template('session_detail.html', response=response)

@app.route('/bills/<session>/<bill_id>/')
def bill_detail(session, bill_id):
    if session not in app.sessions:
        abort(404)
    data = {
        'bill': json.load(json_check('_input/%s/%s.json' % (session, bill_id.upper())))
    }
    if 'title' not in data['bill']:
        abort(404)
    app.page['title'] = data['bill']['title']
    app.page['description'] = 'Details on %s, %s' % ( data['bill']['bill_id'], data['bill']['title'] )
    response = {
        'app': app,
        'session': session,
        'data': data
    }
    return render_template('bill_detail.html', response=response)
