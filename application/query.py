#!/usr/bin/env python
import json
import os
from application import app
from datetime import date, datetime, timedelta
import string

datetimeformat = '%Y-%m-%d %H:%M:%S'

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

class GenericQuery:
    """ Boilerplate Query object.
        Will be used for Committees, Legislators and eventually Bills.
        """

    def get_detail(self, session, item_id):
        """ To load the detail json for the object.
            """
        fn = '_input/%s/%s.json' % (session.lower(), string.replace(item_id.lower(), ' ', '_'))
        return json.load(json_check(fn))

    def filter_session(self, session=None):
        """ Take a session, and, if valid, return the items from that session.
            """
        # If we don't pass it a session it defaults to the current session.
        if not session:
            session = self.session
        filtered = []

        for item in self.items:
            if item['session'].lower() == session.lower():
                filtered.append(item)
        self.items = filtered
        return filtered

    def filter_chamber(self, chamber, items=[]):
        """ Return items from that chamber.
            """
        if len(items) == 0:
            items = self.items
        filtered = []
        for item in items:
            if item['chamber'].lower() == chamber:
                filtered.append(item)
        return filtered

    def filter_updated_at(self, **kwargs):
        """ Return bills that have been updated since 2015 or earlier
            Keyword arguments include day=0 and year=2015 <-- EXPLAIN THIS BETTER***
            """
        filtered = []
        if 'day' in kwargs:
            delta = timedelta(kwargs['day'])
            today = datetime.combine(date.today(), datetime.min.time())
            for item in self.items:
                if datetime.strptime(item['updated_at'], datetimeformat) > ( today - delta ):
                    filtered.append(item)
        elif 'year' in kwargs:
            for item in self.items:
                d = datetime.strptime(item['updated_at'], datetimeformat)
                if d.year > kwargs['year']:
                    filtered.append(item)
        return filtered


class LegislatorQuery(GenericQuery):
    """ A means of querying the list of legislators.
        """

    def __init__(self):
        """
            """
        self.items = json.load(json_check('_input/co-legislators.json'))
        self.bills = json.load(json_check('_input/co-bills-%s.json' % app.session))
        self.committees = json.load(json_check('_input/co-committees.json'))
        self.unfiltered = self.items
        self.session = app.session.upper()

    def get_bills(self, the_id, session):
        """ Get a list of bills that were touched by this legislator.
            Returns a bill object as well as the role the legislator
            had with the bill.
            """
        bills = []
        for bill in self.bills:
            if bill['session'].lower() != session.lower():
                continue
            detail = self.get_detail(bill['session'], bill['bill_id'])
            if 'sponsors' in detail:
                for item in detail['sponsors']:
                    if item['leg_id'] and item['leg_id'].lower() == the_id.lower():
                        bills.append(detail)
        return bills

class CommitteeQuery(GenericQuery):
    """ A means of querying the list of committees.
        """

    def __init__(self):
        """
            """
        self.items = json.load(json_check('_input/co-committees.json'))
        self.bills = json.load(json_check('_input/co-bills-%s.json' % app.session))
        self.legislators = json.load(open('application/static/data/legislators.json'))
        self.unfiltered = self.items
        self.session = app.session.upper()

    def get_bills(self, committee, the_id, session):
        """ Get a list of bills that were touched by this committee.
            Returns a bill object as well as the most-recent item on
            the bill timeline that the committee was involved in.
            """
        bills = []
        for bill in self.bills:
            if bill['session'].lower() != session.lower():
                continue
            detail = self.get_detail(bill['session'], bill['bill_id'])
            if 'actions' in detail:
                for item in detail['actions']:
                    for entity in item['related_entities']:
                        #print committee, entity['name'], the_id, entity['id']
                        if entity['id'] == the_id:
                            bills.append({'bill': detail, 'action': item})
        return bills


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
        self.items = json.load(json_check('_input/co-bills.json'))
        self.legislators = json.load(open('application/static/data/legislators.json'))
        self.unfiltered = self.items
        self.session = app.session.upper()

    def filter_action_dates(self, action_date=None, value=None):
        """ Return bills that have been signed.
            """
        if action_date not in ['passed_upper', 'passed_lower', 'last', 'first', 'signed']:
            return false

        filtered = []
        for item in self.items:
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
        for item in self.items:
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
        for item in self.items:
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
        for item in self.items:
            if datetime.strptime(item['updated_at'], datetimeformat) > ( today - delta ):
                filtered.append(item)
        return filtered

    def filter_sponsored_by(self, legislator):
        """ Return bills that have been sponsored by a particular legislator.
            """
        filtered = []
        for item in self.items:
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
            bills = self.items

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
