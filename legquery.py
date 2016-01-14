#!/usr/bin/env python
import sunlight
import json
import os, sys
import string
from template import Template

class Sunlight:

    def __init__(self):
        """ Initialize the object.
            """
        self.state='co'

    def get_bill_list(self):
        """ Get list of bills.
            """
        self.bills = sunlight.openstates.bills(state=self.state)
        self.session = self.bills[0]['session'].lower()
        print "Session: %s" % self.session
        fh = open('%s-bills-%s.json' % (self.state, self.session), 'wb')
        json.dump(self.bills, fh)
        return True

    def get_session(self):
        """ Return the current session.
            """
        return self.session

    def filter_bills_recent(self, limit = 10):
        """ Filter recent bills.
            """
        return self.bills[:limit]
 
    def get_bill_detail(self, bill_id):
        """ Get bill details for a single bill.
            """
        bill_details = sunlight.openstates.bill_detail(self.state, self.session.upper(), bill_id)
        fh = open('_input/%s/%s.json' % (self.session, string.replace(bill_id.lower(), ' ', '_')), 'wb')
        json.dump(bill_details, fh)
        return bill_details 


def main():
    s = Sunlight()
    s.get_bill_list()

    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/_input' % directory):
        os.mkdir('%s/_input' % directory)
    session = s.get_session()
    if not os.path.isdir('%s/_input/%s' % (directory, session)):
        os.mkdir('%s/_input/%s' % (directory, session))

    bills = s.filter_bills_recent(1000)
    for item in bills:
        details = s.get_bill_detail(item['bill_id'])


if __name__ == '__main__':
	main()
