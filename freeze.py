#!/usr/bin/env python
from datetime import date, timedelta
from optparse import OptionParser
from flask_frozen import Freezer
from application import app, filters
import json
app.debug = False
freezer = Freezer(app)

@freezer.register_generator
def index():
    yield {}

@freezer.register_generator
def week_index():
    yield {}

@freezer.register_generator
def week_detail():
    # Get the weeks we have the weeks for
    current_issue = app.theweek[app.session]
    today = date.today()
    weeks = []
    while current_issue <= today:
        weeks.append(current_issue.__str__())
        current_issue = current_issue + timedelta(7)
    for item in weeks:
        yield { 'issue_date': item }

@freezer.register_generator
def session_index():
    yield {}

@freezer.register_generator
def session_detail():
    for item in app.sessions:
        yield { 'session': item }
        yield { 'session': item, 'js': 'js' }

@freezer.register_generator
def session_passed_index():
    for item in app.sessions:
        for passfail in ['passed', 'failed']:
            yield { 'session': item, 'passfail': passfail }

@freezer.register_generator
def session_signed_detail():
    for item in app.sessions:
        yield { 'session': item }

@freezer.register_generator
def session_passed_detail():
    for item in app.sessions:
        for chamber in ['lower', 'upper']:
            for passfail in ['passed', 'failed']:
                yield { 'session': item,
                        'chamber': chamber,
                        'passfail': passfail
                      }

@freezer.register_generator
def leg_chamber_index():
    for chamber in ['senate', 'house']:
        yield { 'chamber': chamber }

@freezer.register_generator
def leg_district_detail():
    legislators_all = json.load(open('_input/co-legislators.json'))
    for item in legislators_all:
        chamber = filters.chamber_lookup(item['chamber'])
        yield { 'chamber': chamber,
                'district': item['district']
              }

@freezer.register_generator
def legislator_detail():
    legislators_all = json.load(open('_input/co-legislators.json'))
    for item in legislators_all:
        chamber = filters.chamber_lookup(item['chamber'])
        slug = '%s-%s' % (item['last_name'].lower(), item['id'].lower())
        yield { 'chamber': chamber,
                'district': item['district'],
                'slug': slug
              }

@freezer.register_generator
def committee_chamber_index():
    for chamber in ['senate', 'house', 'joint']:
        yield { 'chamber': chamber }

@freezer.register_generator
def committee_detail():
    items = json.load(open('_input/co-committees.json'))
    for item in items:
        slug = filters.get_committee_slug(item['committee'], item['id'].lower())
        chamber = filters.chamber_lookup(item['chamber'])
        yield { 'chamber': chamber,
                'slug': slug
              }

@freezer.register_generator
def bill_detail():
    bills = json.load(open('_input/co-bills.json'))
    for item in bills:
        yield { 'session': item['session'].lower(), 'bill_id': item['bill_id'].lower().replace(' ', '_') }

@freezer.register_generator
def bill_detail_feed():
    bills = json.load(open('_input/co-bills.json'))
    for item in bills:
        yield { 'session': item['session'].lower(), 'bill_id': item['bill_id'].lower().replace(' ', '_') }

if __name__ == '__main__':
    freezer.freeze()
