#!/usr/bin/env python
from flask import g, render_template, url_for, redirect, abort, request
from datetime import datetime, date, timedelta
from collections import OrderedDict
import inspect
import os
import json
import string
from application import app
import filters
from werkzeug.contrib.atom import AtomFeed
from query import CommitteeQuery, BillQuery, LegislatorQuery
# import legislators


datetimeformat = '%Y-%m-%d %H:%M:%S'

def build_url(app, request):
    """ Return a URL for the current view.
        """
    return '%s%s' % (app.url_root, request.path[1:])

# =========================================================
# HOMEPAGE VIEW
# =========================================================

@app.route('/')
def index():
    app.page['title'] = 'Colorado Bill Tracker'
    app.page['description'] = 'Tracking legislation, legislators and committees in the Colorado General Assembly. Updated daily.'
    app.page['url'] = build_url(app, request)

    q = BillQuery()
    q.items = q.filter_session(app.session)

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
# DAY IN REVIEW VIEWS
# =========================================================

def get_session_days(session=None, json=False):
    """ Given the start and end date of the session, get the days there
        were actions on legislation.
        """
    if not session:
        session = app.session
    session_dates = app.session_dates[session]
    # session_dates will look something like [date(2016,1,13), date(2016,5,11)]

    # If we're dealing with the current session, we don't want to return dates
    # in the future.
    today = date.today()
    if today < session_dates[1]:
        session_dates[1] = today

    q = BillQuery()
    q.filter_session(session)

    days = []
    current_issue = session_dates[0]
    while current_issue <= session_dates[1]:
        # Make sure something happened on this day.
        date_range = [current_issue, current_issue]
        bills = q.filter_by_date(date_range, 'ALL')
        if len(bills) > 0:
            if json == True:
                days.append(current_issue.__str__())
            else:
                days.append(current_issue)

        current_issue = current_issue + timedelta(1)
    return days
    
@app.route('/the-day/')
def day_index():
    from recentfeed import RecentFeed
    app.page['title'] = 'Colorado General Assembly daily round-up'
    app.page['description'] = 'A round-up of what happened to which legislation in the Colorado General Assembly.'
    app.page['url'] = build_url(app, request)

    # Get the days we plan on publishing pages for.
    # We don't publish on Saturdays, Sundays, and Mondays if nothing happens.
    # Also, app.session_dates is a list with two items: The first date and the
    # last date of each session.
    current_issue = app.session_dates[app.session][0]
    today = date.today()
    days = json.load(open('_input/days_%s.json' % app.session))

    response = {
        'app': app,
        'days': days,
        #'weeks': weeks
    }
    return render_template('day_index.html', response=response)

@app.route('/the-day/<issue_date>/')
def day_detail(issue_date):
    app.page['title'] = 'in the Colorado state legislature'
    app.page['description'] = 'A round-up of the news, the bills passed, signed and introduced in the Colorado General Assembly on '
    app.page['url'] = build_url(app, request)

    # Make sure it's a valid day
    the_date = datetime.strptime(issue_date, '%Y-%m-%d')
    the_news_date = the_date + timedelta(1)
    date_range = [the_date.date(), the_date.date()]
    days = json.load(open('_input/days_%s.json' % app.session))
    if issue_date not in days:
        abort(404)

    # Get the previous and next days.
    # The beginning and end of the list won't have prev/nexts, so we write
    # logic to make sure we don't throw an error over that.
    pos = days.index(issue_date)
    if pos == 0:
        prev_next = [None, days[pos+1]]
    elif pos == len(days) - 1:
        prev_next = [days[pos-1], None]
    else:
        prev_next = [days[pos-1], days[pos+1]]

    app.page['title'] = '%s %s' % (datetime.strftime(the_date, '%B %-d %Y'), app.page['title'])
    app.page['description'] += '%s' % datetime.strftime(the_date, '%B %-d %Y')

    # Get a json file of the recent legislative news
    news = []
    try:
        #news = json.load(open('_input/news/articles_%s_1.json' % the_date.__str__()))
        news = json.load(open('_input/news/articles_%s_1.json' % issue_date))
    except:
        pass

    q = BillQuery()
    q.filter_session(app.session)
    response = {
        'app': app,
        'issue_date': issue_date,
        'prev_next': prev_next,
        'news': news,
        'signed': q.filter_by_date(date_range, 'signed', q.filter_action_dates('signed')),
        'introduced': q.filter_by_date(date_range, 'first', q.filter_action_dates('first')),
        'passed_upper': q.filter_by_date(date_range, 'passed_upper', q.filter_action_dates('passed_upper')),
        'passed_lower': q.filter_by_date(date_range, 'passed_lower', q.filter_action_dates('passed_lower')),
    }
    return render_template('day_detail.html', response=response)

# =========================================================
# WEEK IN REVIEW VIEWS
# =========================================================

def get_session_weeks(session=None, json=False):
    """ Given the start and end date of the session, get the weeks we
        published Week in Reviews.
        """
    if not session:
        session = app.session
    session_dates = app.session_dates[session]

    # If we're dealing with the current session, we don't want to return date
    # in the future.
    today = date.today()
    if today < session_dates[1]:
        session_dates[1] = today

    current_issue = app.theweek[app.session]
    today = date.today()
    weeks = []
    while current_issue <= today:
        if json == True:
            weeks.append(current_issue.__str__())
        else:
            weeks.append(current_issue)
        current_issue = current_issue + timedelta(7)

    return weeks

@app.route('/the-week/')
def week_index():
    from recentfeed import RecentFeed
    app.page['title'] = 'Colorado General Assembly weekly round-ups'
    app.page['description'] = 'A round-up of what happened to which legislation in the Colorado General Assembly.'
    app.page['url'] = build_url(app, request)

    # Get the weeks we have the weeks for
    weeks = get_session_weeks()

    response = {
        'app': app,
        'weeks': weeks
    }
    return render_template('week_index.html', response=response)

@app.route('/the-week/<issue_date>/')
def week_detail(issue_date):
    app.page['title'] = 'The Week in Colorado legislature, '
    app.page['description'] = 'A round-up of what happened to which legislation in Colorado\'s state legislature for the week ending '
    app.page['url'] = build_url(app, request)

    # Make sure it's a valid week
    current_issue = app.theweek[app.session]
    today = date.today()
    weeks = []
    while current_issue <= today:
        weeks.append(current_issue.__str__())
        current_issue = current_issue + timedelta(7)

    # Get the previous and next days.
    # The beginning and end of the list won't have prev/nexts, so we write
    # logic to make sure we don't throw an error over that.
    pos = weeks.index(issue_date)
    if pos == 0:
        if len(weeks) == 1:
            prev_next = [None, None]
        else:
            prev_next = [None, weeks[pos+1]]
    elif pos == len(weeks) - 1:
        prev_next = [weeks[pos-1], None]
    else:
        prev_next = [weeks[pos-1], weeks[pos+1]]

    # Turn the date into a range
    the_date = datetime.strptime(issue_date, '%Y-%m-%d')
    start, finish = the_date - timedelta(7), the_date
    date_range = [start.date(), finish.date()]

    app.page['description'] += '%s' % datetime.strftime(the_date, '%B %-d %Y')
    app.page['title'] += '%s' % datetime.strftime(the_date, '%B %-d %Y')

    if issue_date not in weeks:
        abort(404)

    # Get a json file of the recent legislative news
    news = []
    try:
        news = json.load(open('_input/news/articles_%s_8.json' % issue_date))
    except:
        try:
            news = json.load(open('_input/news/articles_%s_7.json' % issue_date))
        except:
            news = []

    q = BillQuery()
    q.filter_session(app.session)
    response = {
        'app': app,
        'issue_date': issue_date,
        'prev_next': prev_next,
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
    app.page['url'] = build_url(app, request)

    q = CommitteeQuery()
    q.items = q.filter_updated_at(year=2015)
    data = {
        'committees': {
            'all': q.items,
            'joint': q.filter_chamber('joint'),
            'senate': q.filter_chamber('upper'),
            'house': q.filter_chamber('lower')
        }
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
    chamber_for_query = 'joint'
    if chamber == 'senate':
        chamber_for_query = 'upper'
    elif chamber == 'house':
        chamber_for_query = 'lower'
    app.page['title'] = 'Colorado %s committees' % chamber_pretty
    app.page['description'] = 'An index of the committees in Colorado state %s.' % chamber_pretty
    app.page['url'] = build_url(app, request)

    q = CommitteeQuery()
    q.items = q.filter_chamber(chamber_for_query)
    q.items = q.filter_updated_at(year=2015)
    data = {
        'committees': q.items
    }
    response = {
        'app': app,
        'chamber': chamber_pretty,
        #'json': json.dumps(),
        'data': data
    }
    return render_template('committee_chamber_index.html', response=response)

@app.route('/committees/<chamber>/<slug>/<session>/')
@app.route('/committees/<chamber>/<slug>/')
def committee_detail(chamber, slug, session='2017a'):   #***HC
    chamber_pretty = filters.chamber_lookup(chamber).capitalize()

    # A slug usually looks like "business-labor-and-technology-coc000109"
    # The committee id is the string after the final hyphen.
    c_id = slug.split('-')[-1]
    data = {
        'committee': json.load(open('_input/%s/%s.json' % (session, c_id)))
    }

    # Get the bills the committee has touched.
    q = CommitteeQuery()
    data['bills'] = q.get_bills(data['committee']['committee'], c_id.upper(), session)

    app.page['title'] = 'Colorado %s %s committee' % (chamber_pretty, data['committee']['committee'])
    if chamber_pretty in data['committee']['committee']:
        app.page['title'] = '%s committee' % data['committee']['committee']
    app.page['description'] = 'Details on the %s, including legislation, leadership and members' % app.page['title']
    app.page['url'] = build_url(app, request)

    response = {
        'app': app,
        'chamber': chamber,
        #'json': json.dumps(),
        'data': data
    }
    return render_template('committee_detail.html', response=response)

# =========================================================
# LEGISLATION VIEWS
# =========================================================

@app.route('/bills.<js>')
@app.route('/bills/')
def session_index(js=''):
    app.page['title'] = 'Search Colorado General Assembly legislation'
    app.page['description'] = 'An index of Colorado legislative sessions we have bills for. Also, search all bills. Also, use our Bill Generator.'
    app.page['url'] = build_url(app, request)

    q = BillQuery()
    data = {
        'bills': q.items
    }

    # We return a lighter version of the bills dict for generating the javascript.
    data['bills_light'] = []
    for item in data['bills']:
        url = 'http://extras.denverpost.com/app/bill-tracker/bills/%s/%s/' % (item['session'].lower(), item['bill_id'].replace(' ', '_').lower())
        d = { 'title': item['title'], 'url': url, 'session': item['session'] }
        data['bills_light'].append(d)

    response = {
        'app': app,
        'data': data,
        'json': json.dumps(data['bills_light']),
    }

    fn = 'session_index.html'
    if js == 'js':
        fn = fn.replace('.html', '.js')
    return render_template(fn, response=response)

@app.route('/bills/<session>.<js>')
@app.route('/bills/<session>/')
def session_detail(session, js='', csv=''):
    if session not in app.sessions:
        abort(404)
    app.page['title'] = 'Session %s' % session
    app.page['description'] = ''
    app.page['url'] = build_url(app, request)

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
    data = {
        'bill': json.load(open('_input/%s/%s.json' % (session, bill_id.lower())))
    }
    chamber = 'Senate'
    if data['bill']['bill_id'][0] == 'H':
        chamber = 'House'
    app.page['title'] = '%s - %s' % (data['bill']['title'], data['bill']['bill_id'])
    app.page['description'] = 'Details on Colorado %s %s %s, %s' % ( chamber, data['bill']['type'][0], data['bill']['bill_id'], data['bill']['title'] )
    app.page['url'] = build_url(app, request)
    response = {
        'app': app,
        'chamber': chamber,
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

@app.route('/bills/<session>/signed/')
def session_signed_detail(session):
    if session not in app.sessions:
        abort(404)

    app.page['title'] = 'Legislation Colorado\'s governor signed into law in the %s session' % session
    app.page['description'] = 'A list of legislation passed into law in the %s session' % session
    app.page['url'] = build_url(app, request)

    q = BillQuery()
    q.session = session.upper()
    q.filter_session()
    data = {
        'bills': q.filter_action_dates('signed'),
    }
    response = {
        'app': app,
        'data': data,
        'session': session,
    }
    return render_template('session_signed_detail.html', response=response)

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
    app.page['url'] = build_url(app, request)

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
    app.page['url'] = build_url(app, request)

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

# =========================================================
# LEGISLATOR VIEWS
# =========================================================

@app.route('/legislators/')
def leg_index():
    app.page['title'] = 'Colorado legislators'
    app.page['description'] = 'An index of Colorado legislators'
    app.page['url'] = build_url(app, request)
    legislators = json.load(open('_input/co-legislators.json'))
    response = {
        'app': app,
        'legislators': legislators
    }
    return render_template('leg_index.html', response=response)

@app.route('/legislators/<chamber>/')
def leg_chamber_index(chamber):
    title = 'Senator'
    if chamber == 'house':
        title = 'Representative'

    app.page['title'] = 'Colorado State %ss' % title
    app.page['description'] = 'An index of Colorado %ss in the state General Assembly' % title
    app.page['url'] = build_url(app, request)
    legislators = json.load(open('_input/co-legislators.json'))
    response = {
        'app': app,
        'chamber': chamber,
        'legislators': legislators
    }
    return render_template('leg_chamber_index.html', response=response)

@app.route('/legislators/<chamber>/<district>/')
def leg_district_detail(district, chamber):
    chamber_query = 'upper'
    if chamber == 'house':
        chamber_query = 'lower'

    app.page['title'] = 'Colorado %s district %s' % (chamber.title(), district)
    app.page['description'] = ''
    app.page['url'] = build_url(app, request)
    legislators_all = json.load(open('_input/co-legislators.json'))

    # Figure out which legislators are in the district we're looking at.
    legislators = []
    for item in legislators_all:
        if item['chamber'].lower() == chamber_query and item['district'] == district:
            legislators.append(item)

    response = {
        'app': app,
        'chamber': chamber,
        'district': district,
        'legislators': legislators,
    }
    return render_template('leg_district_detail.html', response=response)

@app.route('/legislators/<chamber>/<district>/<slug>/')
def legislator_detail(district, slug, chamber):
    title = 'Senator'
    if chamber == 'house':
        title = 'Representative'

    # Figure out which legislator we're looking for
    # A slug usually looks like "hammajamma-col000109"
    # The legislator id is the string after the final hyphen.
    l_id = slug.split('-')[-1]

    # **** Need to fix the code below come the 2019 session.
    try:
        legislator = json.load(open('_input/2017a/%s.json' % l_id.lower()))
    except:
        legislator = json.load(open('_input/2016a/%s.json' % l_id.lower()))
    legislator['occupation'] = legislator['+occupation']

    # Get the bills the legislator has touched.
    q = LegislatorQuery()
    legislator['sponsored'] = q.get_bills(l_id.upper(), app.session)

    app.page['title'] = '%s %s is a Colorado state %s' % (legislator['first_name'], legislator['last_name'], title)
    app.page['description'] = '%s %s contact and legislation information for this Colorado state %s' % (legislator['first_name'], legislator['last_name'], title)
    app.page['url'] = build_url(app, request)

    response = {
        'app': app,
        'title': title,
        'chamber': chamber,
        'legislator': legislator
    }
    return render_template('legislator_detail.html', response=response)

@app.route('/updates.atom')
def recent_feed():
    stamp = datetime.today().strftime('%Y%m%d')
    url='http://extras.denverpost.com/app/bill-tracker/?date%s' % stamp
    feed = AtomFeed('Colorado Bill Tracker Updates',
                    feed_url=url, url=url)
    feed.add('Bill Tracker updated with the most-recent legislation information.', '',
             content_type='html',
             url=url,
             updated=datetime.today(),
             published=datetime.today())
    return feed.get_response()

# =========================================================
# === NOT DEPLOYED YET === #
# =========================================================

