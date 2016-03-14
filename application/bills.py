#!/usr/bin/env python
from flask import g, render_template, url_for, redirect, abort, request
from datetime import datetime, date, timedelta
from collections import OrderedDict
import json
import inspect
import os
import string
from application import app
import filters
from datetime import date, datetime, timedelta
from werkzeug.contrib.atom import AtomFeed
# import legislators


datetimeformat = '%Y-%m-%d %H:%M:%S'

class GenericQuery:
    """ Boilerplate Query object.
        Will be used for Committees, Legislators and eventually Bills.
        """

    def get_detail(self, session, item_id):
        """ To load the detail json for the object.
            """
        fn = '_input/%s/%s.json' % (session.lower(), string.replace(item_id.lower(), ' ', '_'))
        return json.load(json_check(fn))

    def filter_session(self, session):
        """ Take a session, and, if valid, return the items from that session.
            """
        # If we don't pass it a session it defaults to the current session.
        if not session:
            session = self.session
        filtered = []

        for item in self.items:
            if item['session'] == session:
                filtered.append(item)
        self.items = filtered
        return filtered

    def filter_chamber(self, chamber):
        """ Return items from that chamber.
            """
        filtered = []
        for item in self.items:
            if item['chamber'].lower() == chamber:
                filtered.append(item)
        return filtered

class CommitteeQuery(GenericQuery):
    """ A means of querying the list of committees.
        """

    def __init__(self):
        """
            """
        self.items = json.load(json_check('_input/co-committees.json'))
        self.legislators = json.load(open('application/static/data/legislators.json'))
        self.unfiltered = self.items
        self.session = app.session.upper()

class BillQuery(GenericQuery):
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
        self.legislators = json.load(open('application/static/data/legislators.json'))
        self.unfiltered = self.bills
        self.session = app.session.upper()

    def filter_action_dates(self, action_date=None, value=None):
        """ Return bills that have been signed.
            """
        if action_date not in ['passed_upper', 'passed_lower', 'last', 'first', 'signed']:
            return false

        filtered = []
        for item in self.bills:
            detail = self.get_detail(item['session'], item['bill_id'])
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
            detail = self.get_detail(self.session, item['bill_id'])
            if detail and 'votes' in detail:
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
            detail = self.get_detail(self.session, item['bill_id'])
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
        filtered = []
        delta = timedelta(day)
        today = datetime.combine(date.today(), datetime.min.time())
        for item in self.bills:
            if datetime.strptime(item['updated_at'], datetimeformat) > ( today - delta ):
                filtered.append(item)
        return filtered

    def filter_sponsored_by(self, legislator):
        """ Return bills that have been sponsored by a particular legislator.
            """
        filtered = []
        for item in self.bills:
            detail = self.get_detail(self.session, item['bill_id'])
            for sponsor in detail['sponsors']:
                # *** this probably isn't how it will really work.
                if sponsor['name'].lower() == legislator:
                    filtered.append(item)
        return filtered

    def filter_by_date(self, date_range, field='last', bills=[]):
        """ Return bills that have an action date within the date_range.
            This is more accurate than the filter_updated_at because this date
            is the date there was any action on the bill and updated_at is just
            the timestamp when the Sunlight Foundation last modified it.

            Available fields:
            'passed_upper', 'passed_lower', 'last', 'signed', 'first'
            """
        if len(bills) == 0:
            bills = self.bills

        filtered = []
        for item in bills:
            detail = self.get_detail(item['session'], item['bill_id'])
            if 'action_dates' in detail and field in detail['action_dates'] and datetimeformat:
                if not detail['action_dates'][field]:
                    continue
                dt = datetime.strptime(detail['action_dates'][field], datetimeformat)
                if date_range[0] <= dt.date() <= date_range[1]:
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
    app.page['title'] = 'Colorado Bill Tracker'
    app.page['description'] = 'Tracking legislation in Colorado\'s state senate and house.'
    q = BillQuery()
    q.filter_session()

    days_back = 0
    bills = []
    finish = date.today()
    start = finish - timedelta(days_back)
    while True:
        bills = q.filter_by_date([start, finish], 'last')
        if len(bills) > 0:
            break
        if days_back > 300:
            break
        days_back += 1
        start = finish - timedelta(days_back)

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

# =========================================================
# WEEK IN REVIEW VIEWS
# =========================================================

@app.route('/the-week/')
def week_index():
    from recentfeed import RecentFeed
    app.page['title'] = 'Colorado state legislature weekly round-ups'
    app.page['description'] = 'A round-up of what happened to which legislation in Colorado\'s state legislature.'

    # Get the weeks we have the weeks for
    current_issue = app.theweek[app.session]
    today = date.today()
    weeks = []
    while current_issue <= today:
        weeks.append(current_issue)
        current_issue = current_issue + timedelta(7)

    response = {
        'app': app,
        'weeks': weeks
    }
    return render_template('week_index.html', response=response)

@app.route('/the-week/<issue_date>/')
def week_detail(issue_date):
    app.page['title'] = 'The Week in the Colorado legislature'
    app.page['description'] = 'A round-up of what happened to which legislation in Colorado\'s state legislature.'

    # Make sure it's a valid week
    current_issue = app.theweek[app.session]
    today = date.today()
    weeks = []
    while current_issue <= today:
        weeks.append(current_issue.__str__())
        current_issue = current_issue + timedelta(7)

    # Turn the date into a range
    the_date = datetime.strptime(issue_date, '%Y-%m-%d')
    start, finish = the_date - timedelta(7), the_date
    date_range = [start.date(), finish.date()]
    print start, finish

    if issue_date not in weeks:
        abort(404)

    # Get a json file of the recent legislative news
    news = []
    try:
        news = json.load(open('_input/news/articles_%s_8.json' % issue_date))
    except:
        news = json.load(open('_input/news/articles_%s_7.json' % issue_date))

    q = BillQuery()
    q.filter_session()
    response = {
        'app': app,
        'issue_date': issue_date,
        'news': news,
        'signed': q.filter_by_date(date_range, 'signed', q.filter_action_dates('signed')),
        'introduced': q.filter_by_date(date_range, 'first', q.filter_action_dates('first')),
        'passed_upper': q.filter_by_date(date_range, 'passed_upper', q.filter_action_dates('passed_upper')),
        'passed_lower': q.filter_by_date(date_range, 'passed_lower', q.filter_action_dates('passed_lower')),
    }
    return render_template('week_detail.html', response=response)

# =========================================================
# COMMITTEE VIEWS
# =========================================================

@app.route('/committees/')
def committee_index(chamber=''):
    app.page['title'] = 'Colorado legislative committees'
    app.page['description'] = 'An index of the committees in Colorado legislature.'
    q = CommitteeQuery()
    data = {
        'committees': q.items
    }
    response = {
        'app': app,
        #'json': json.dumps(),
        'data': data
    }
    return render_template('committee_index.html', response=response)

@app.route('/committees/<chamber>/')
def committee_chamber_index(chamber):
    chamber_pretty = filters.chamber_lookup(chamber).capitalize()
    app.page['title'] = 'Colorado %s committees' % chamber_pretty
    app.page['description'] = 'An index of the committees in Colorado state %s.' % chamber_pretty
    q = CommitteeQuery()
    q.items = q.filter_chamber(chamber)
    data = {
        'committees': q.items
    }
    response = {
        'app': app,
        #'json': json.dumps(),
        'data': data
    }
    return render_template('committee_index.html', response=response)

@app.route('/committees/<chamber>/<slug>/')
def committee_detail(chamber, slug):
    chamber_pretty = filters.chamber_lookup(chamber).capitalize()
    committee = ''
    app.page['title'] = 'Colorado %s committees' % chamber_pretty
    app.page['description'] = 'An index of the committees in Colorado state %s.' % chamber_pretty
    q = CommitteeQuery()
    q.items = q.filter_chamber(chamber)
    data = {
        'committees': q.items
    }
    response = {
        'app': app,
        #'json': json.dumps(),
        'data': data
    }
    return render_template('committee_detail.html', response=response)

# =========================================================
# LEGISLATION VIEWS
# =========================================================

@app.route('/bills/')
def session_index():
    app.page['title'] = 'Legislative Sessions'
    app.page['description'] = 'An index of Colorado legislative sessions we have bills for.'
    response = {
        'app': app,
    }
    return render_template('session_index.html', response=response)

@app.route('/bills/<session>.<js>')
@app.route('/bills/<session>.<csv>')
@app.route('/bills/<session>/')
def session_detail(session, js='', csv=''):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Session %s' % session
    app.page['description'] = ''
    q = BillQuery()
    q.filter_session(session.upper())
    data = {
        'bills': q.filter_action_dates('first')
    }

    # Clean up the json for delivering to datatables.
    # Datatables requires all fields be present in all items,
    # which means we need to add vote fields for the bills that haven't
    # been voted on yet.
    bills = []
    for item in data['bills']:
        if 'votes' not in item:
            item['votes'] = []
        if 'sources' not in item:
            item['sources'] = []
        bills.append(item)

    # We return a lighter version of the bills dict for generating the javascript.
    data['bills_light'] = []
    for item in data['bills']:
        url = 'http://extras.denverpost.com/app/bill-tracker/bills/%s/%s/' % (item['session'].lower(), item['bill_id'].replace(' ', '_').lower())
        d = { 'title': item['title'], 'url': url }
        data['bills_light'].append(d)

    response = {
        'app': app,
        'session': session,
        'json': json.dumps(bills),
        'data': data
    }

    fn = 'session_detail.html'
    if js == 'js':
        fn = fn.replace('.html', '.js')
    elif csv == 'csv':
        fn = fn.replace('.html', '.csv')
    return render_template(fn, response=response)

@app.route('/bills/<session>/<bill_id>/')
def bill_detail(session, bill_id):
    if session not in app.sessions:
        abort(404)
    billdata = json.load(open('_input/%s/%s.json' % (session, bill_id.lower())))
    data = {
        'bill': billdata
    }
    app.page['title'] = '%s - %s' % (data['bill']['title'], data['bill']['bill_id'])
    app.page['description'] = 'Details on %s, %s' % ( data['bill']['bill_id'], data['bill']['title'] )
    response = {
        'app': app,
        'session': session,
        'data': data
    }
    return render_template('bill_detail.html', response=response)

@app.route('/bills/<session>/<bill_id>/updates.atom')
def bill_detail_feed(session, bill_id):
    if session not in app.sessions:
        abort(404)
    bill = json.load(open('_input/%s/%s.json' % (session, bill_id.lower())))
    feed = AtomFeed('%s - %s' % (bill['title'], bill['bill_id']),
                    feed_url=request.url.replace(request.url_root, app.url_root), url=app.url_root)

    # That "[:-1]" bit below is so we don't get double-slashes in the url path
    permalink = '%s%s' % (app.url_root[:-1], request.path.replace('updates.atom', ''))
    for item in bill['actions']:
        feed.add('%s: %s' % (bill['bill_id'], item['action']), '',
                 content_type='html',
                 url=permalink,
                 updated=filters.datetime_raw_filter(item['date']),
                 published=filters.datetime_raw_filter(item['date']))
    return feed.get_response()

@app.route('/bills/<session>/passed/')
@app.route('/bills/<session>/failed/')
def session_passed_index(session, passfail=''):
    if session not in app.sessions:
        abort(404)

    # This logic allows us to override the view if we need to,
    # like we need to when we're deploying automatically from freeze.py
    if passfail == '':
        passfail = 'passed'
        if 'failed' in request.path:
            passfail = 'failed'
    app.page['title'] = 'Legislation that %s in the %s session' % (passfail, session)
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
    app.page['title'] = 'Legislation that %s the %s chamber in the %s session' % (passfail, chamber, session)
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

# === NOT DEPLOYED YET === #

@app.route('/senate/')
@app.route('/house/')
def chamber_index(chamber=''):
    if chamber == '':
        chamber = 'senate'
        if 'house' in request.path:
            chamber = 'house'
    app.page['title'] = 'Colorado State %s legislators' % chamber.title()
    app.page['description'] = 'An index of Colorado legislators in the state %s' % chamber
    legislators = json.load(open('application/static/data/legislators.json'))
    response = {
        'app': app,
        'chamber': chamber,
    }
    return render_template('chamber_index.html', response=response)

@app.route('/senate/<district>/')
@app.route('/house/<district>/')
def district_detail(district, chamber=''):
    if chamber == '':
        chamber = 'senate'
        if 'house' in request.path:
            chamber = 'house'
    app.page['title'] = 'Colorado %s district %s' % (chamber.title(), district)
    app.page['description'] = ''
    legislators_all = json.load(open('application/static/data/legislators.json'))

    # Figure out which legislators are in the district we're looking at.
    legislators = []
    for item in legislators_all:
        if legislators_all[item]['chamber'].lower() == chamber and legislators_all[item]['district'] == district:
            legislators.append(legislators_all[item])

    response = {
        'app': app,
        'legislators': legislators,
    }
    return render_template('district_detail.html', response=response)

@app.route('/senate/<district>/<last_name>/')
@app.route('/house/<district>/<last_name>/')
def legislator_detail(district, last_name, chamber=''):
    title = 'senator'

    # Allow us to override the request.path with a passed argument.
    # This is used in freeze.py in our deploy.
    if chamber == '':
        chamber = 'senate'
        if 'house' in request.path[:10]:
            chamber = 'house'
            title = 'representative'
    elif chamber == 'house':
        # A little bit of repetition, sorry.
        title = 'representative'

    legislators_all = json.load(open('application/static/data/legislators.json'))

    legislator = []
    # Figure out which legislator we're looking for
    last_name = last_name.replace('_', ' ').title()
    if ' ' in last_name:
        last_name += '.'
    for item in legislators_all:
        if item == last_name:
            legislator = legislators_all[item]
            print legislator
    app.page['title'] = '%s %s, Colorado state %s' % (legislator['name_first'], legislator['name_last'], title)
    app.page['description'] = '%s %s contact and legislation information for this Colorado state %s' % (legislator['name_first'], legislator['name_last'], title)

    response = {
        'app': app,
        'title': title,
        'legislator': legislator
    }
    return render_template('legislator_detail.html', response=response)

@app.route('/updates.atom')
def recent_feed():
    url='http://extras.denverpost.com/app/bill-tracker/'
    feed = AtomFeed('Colorado Bill Tracker Updates',
                    feed_url=url, url=url)
    feed.add('Bill Tracker updated with the most-recent legislation information.', '',
             content_type='html',
             url=url,
             updated=datetime.today(),
             published=datetime.today())
    return feed.get_response()
