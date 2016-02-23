#!/usr/bin/env python
from datetime import date, timedelta
from optparse import OptionParser
from flask_frozen import Freezer
from application import app
import json
app.debug = False
freezer = Freezer(app)


"""
@freezer.register_generator
def freezeit():
    for year in ['', 2014]:
        for item in app.crime_children:
            for crime in app.crime_children[item]:
                if year == '':
                    yield {'crimeparent': item, 'crime': crime }
                else:
                    yield {'crimeparent': item, 'crime': crime, 'year': year}
        for item in app.crime_launched:
            if item == 'violent-crime':
                item = 'violent'
            try:
                if year == '':
                    yield {'crime': item}
                else:
                    yield {'crime': item, 'year': year}
            except:
                pass
"""

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
    while current_issue < today:
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

@freezer.register_generator
def session_passed_index():
    for item in app.sessions:
        for passfail in ['passed', 'failed']:
            yield { 'session': item, 'passfail': passfail }

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
def bill_detail():
    bills = json.load(open('_input/co-bills.json'))
    for item in bills:
        yield { 'session': item['session'].lower(), 'bill_id': item['bill_id'].lower().replace(' ', '_') }

if __name__ == '__main__':
    freezer.freeze()
