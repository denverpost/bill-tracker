#!/usr/bin/env python
from flask import g, render_template, url_for, redirect, abort
from datetime import datetime, date, timedelta
from collections import OrderedDict
import json
import inspect
import os
import string
from application import app
import filters

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

    def get_bill_detail(self, session, bill_id):
        """ For when we need to query a field in the bill details.
            """
        return json.load(json_check('_input/%s/%s.json' % (session.lower(), string.replace(bill_id.lower(), ' ', '_'))))

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

    def filter_action_dates(self, action_date=None, value=None):
        """ Return bills that have been signed.
            """
        if action_date not in ['passed_upper', 'passed_lower', 'last', 'first', 'signed']:
            return false

        filtered = []
        for item in self.bills:
            detail = self.get_bill_detail(self.session, item['bill_id'])
            if detail:
                # Append the action dates to the item so we don't have
                # to look them up again later.
                if 'action_dates' in detail:
                    item['action_dates'] = detail['action_dates']
                if 'votes' in detail and detail['votes'] != []:
                    item['votes'] = detail['votes']
                if value:
                    if detail['action_dates'][action_date] == value:
                        filtered.append(item)
                elif 'action_dates' in detail and detail['action_dates'][action_date]:
                    filtered.append(item)

        sorts = sorted(filtered, key=lambda x:x['action_dates'][action_date], reverse=True)
        return sorts

    def filter_failed(self):
        """ Return bills that have failed in the house and / or senate.
            """
        filtered = []
        for item in self.bills:
            detail = self.get_bill_detail(self.session, item['bill_id'])
            if detail:
                if len(detail['votes']) == 0:
                    continue
                if detail['votes'][0]['yes_count'] < detail['votes'][0]['no_count']:
                    filtered.append(item)

        sorts = sorted(filtered, key=lambda x:x['action_dates']['first'], reverse=True)
        return sorts

    def filter_close_vote(self, chamber):
        """ Return bills that have passed a chamber with a slim margin.
            """
        threshold = 5
        if chamber == 'upper':
            threshold = 3

        filtered = []
        for item in self.bills:
            detail = self.get_bill_detail(self.session, item['bill_id'])
            if not detail['action_dates']['passed_%s' % chamber]:
                continue
            if detail:
                if abs(detail['votes'][0]['yes_count'] - detail['votes'][0]['no_count']) < threshold:
                    filtered.append(item)

        sorts = sorted(filtered, key=lambda x:x['action_dates']['passed_%s' % chamber], reverse=True)
        return sorts

    def filter_updated_at(self, day=0):
        """ Return bills that have been updated within the last X days.
            """
        from datetime import date, datetime, timedelta
        filtered = []
        delta = timedelta(day)
        today = datetime.combine(date.today(), datetime.min.time())
        for item in self.bills:
            if datetime.strptime(item['updated_at'], datetimeformat) > ( today - delta ):
                #print datetime.strptime(item['updated_at'], datetimeformat)
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
    q.filter_session()

    days_back = 0
    bills = []
    while True:
        bills = q.filter_updated_at(days_back)
        if len(bills) > 0:
            break
        if days_back > 300:
            break
        #print days_back,
        days_back += 1

    #print len(bills)
    
    response = {
        'app': app,
        'bills': bills,
        'signed': q.filter_action_dates('signed'),
        'introduced': q.filter_action_dates('first'),
        'passed_upper': q.filter_action_dates('passed_upper'),
        'passed_lower': q.filter_action_dates('passed_lower'),
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
    app.page['title'] = 'Session %s' % session
    app.page['description'] = ''
    q = BillQuery()
    q.filter_session(session.upper())
    data = {
        'bills': q.filter_action_dates('first')
    }
    response = {
        'app': app,
        'session': session,
        'data': data
    }
    return render_template('session_detail.html', response=response)

@app.route('/bills/<session>/<passfail>/')
def session_passed_index(session, passfail):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Bills that %s in the %s session' % (passfail, session)
    app.page['description'] = ''
    response = {
        'app': app,
        'session': session,
        'passfail': passfail,
    }
    return render_template('session_passed_index.html', response=response)

@app.route('/bills/<session>/<passfail>/<chamber>/')
def session_passed_detail(session, passfail, chamber):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Bills that %s the %s chamber in the %s session' % (passfail, chamber, session)
    app.page['description'] = ''
    q = BillQuery()
    q.session = session.upper()
    q.filter_session()
    data = {
        'upper': q.filter_action_dates('passed_upper'),
        'lower': q.filter_action_dates('passed_lower'),
    }
    if passfail == 'failed':
        data = {
            'upper': q.filter_failed(),
            'lower': q.filter_failed(),
        }
    response = {
        'app': app,
        'session': session,
        'passfail': passfail,
        'chamber': chamber,
        'data': data
    }
    return render_template('session_passed_detail.html', response=response)

# *** FIGURE OUT WHICH BILLS HAVE FAILED

@app.route('/bills/<session>/<bill_id>/')
def bill_detail(session, bill_id):
    if session not in app.sessions:
        abort(404)
    data = {
        'bill': json.load(json_check('_input/%s/%s.json' % (session, bill_id.upper())))
    }
    if 'title' not in data['bill']:
        abort(404)
    app.page['title'] = '%s - %s' % (data['bill']['title'], data['bill']['bill_id'])
    app.page['description'] = 'Details on %s, %s' % ( data['bill']['bill_id'], data['bill']['title'] )
    response = {
        'app': app,
        'session': session,
        'data': data
    }
    return render_template('bill_detail.html', response=response)

# === NOT DEPLOYED YET === #

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

