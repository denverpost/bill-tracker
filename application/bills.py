#!/usr/bin/env python
from flask import g, render_template, url_for, redirect, abort
from datetime import datetime, date, timedelta
from collections import OrderedDict
import json
import inspect
import os
from application import app

datetimeformat = '%Y-%m-%d %H:%M:%S'

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
        self.unfiltered = self.bills
        self.session = app.session.upper()

    def filter_session(self, session=None):
        """ Take a session, and, if valid, return the bills form that session.
            """
        # If we don't pass it a session it defaults to the current session.
        if not session:
            session = self.session
        filtered = []

        for item in self.bills:
            if item['session'] == session:
                filtered.append(item)
        self.bills = filtered
        return filtered

    def filter_updated_at(self, day=0):
        """ Return bills that have been updated within the last X days.
            """
        from datetime import date, datetime, timedelta
        filtered = []
        delta = timedelta(day)
        d = date.today()
        today = datetime.combine(d, datetime.min.time())
        for item in self.bills:
            if datetime.strptime(item['updated_at'], datetimeformat) > ( today - delta ):
                print datetime.strptime(item['updated_at'], datetimeformat)
                filtered.append(item)
            else:
                print len(self.bills), datetime.strptime(item['updated_at'], datetimeformat), ( today - delta )
        self.bills = filtered
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
    q.filter_session()

    days_back = 0
    bills = []
    while True:
        bills = q.filter_updated_at(days_back)
        if len(bills) > 0:
            break
        if days_back > 300:
            break
        print days_back,
        days_back += 1

    print len(bills)
    
    response = {
        'app': app,
        'bills': bills,
        'days_back': days_back,
        'back_date': date.today() - timedelta(days_back)
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
    q = BillQuery()
    data = {
        'bills': q.filter_session(session.upper())
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

@app.route('/bills/<session>/legislators/')
def legislator_index(session):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Legislators'
    app.page['description'] = 'An index of Colorado statehouse legislators and which bills they sponsored.'
    response = {
        'app': app,
    }
    return render_template('legislator_index.html', response=response)

@app.route('/bills/<session>/legislators/<legislator>/')
def legislator_detail(session, legislator):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Legislator'
    app.page['description'] = ''
    response = {
        'app': app,
    }
    return render_template('legislator_detail.html', response=response)

