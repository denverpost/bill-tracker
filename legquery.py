#!/usr/bin/env python
import sunlight
import json
import doctest
import os, sys
import string
import argparse

class Sunlight:

    def __init__(self):
        """ Initialize the object.
            >>> s = Sunlight()
            """
        self.state='co'
        self.directory = os.path.dirname(os.path.realpath(__file__))

    def get_bill_list(self, session=None):
        """ Get list of bills, sometimes from a particular session.
            >>> s = Sunlight()
            """
        if session:
            self.bills = sunlight.openstates.bills(state=self.state, session=session.upper())
            filename = '_input/%s-bills-%s.json' % (self.state, session.lower())
        else:
            self.bills = sunlight.openstates.bills(state=self.state)
            filename = '_input/%s-bills.json' % (self.state)

        self.session = self.bills[0]['session'].lower()
        print "Session: %s" % self.session
        fh = open(filename, 'wb')
        json.dump(self.bills, fh)
        return True

    def filter_bills_recent(self, limit = 10):
        """ Filter recent bills.
            >>> s = Sunlight()
            """
        return self.bills[:limit]
 
    def get_bill_detail(self, bill_id):
        """ Get bill details for a single bill.
            >>> s = Sunlight()
            """
        if not os.path.isdir('%s/_input/%s' % (self.directory, self.session)):
            os.mkdir('%s/_input/%s' % (self.directory, self.session))
        bill_details = sunlight.openstates.bill_detail(self.state, self.session.upper(), bill_id)
        fh = open('_input/%s/%s.json' % (self.session, string.replace(bill_id.lower(), ' ', '_')), 'wb')
        json.dump(bill_details, fh)
        return bill_details 


def main(args):
    s = Sunlight()
    s.get_bill_list(args.session)

    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/_input' % directory):
        os.mkdir('%s/_input' % directory)

    bills = s.filter_bills_recent(int(args.limit))
    i = 0
    for item in bills:
        i += 1
        print i, item['bill_id']
        try:
            details = s.get_bill_detail(item['bill_id'])
        except:
            print item['session']
            s.session = item['session'].lower()
            details = s.get_bill_detail(item['bill_id'])



def build_parser():
    """ This method allows us to test the args.
        """
    parser = argparse.ArgumentParser(usage='$ python legquery.py',
                                     description='Download data from Sunlight and update bill indexes.',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-c", "--cache", dest="cache", default=False, action="store_true")
    parser.add_argument("-s", "--session", dest="session")
    parser.add_argument("-l", "--limit", dest="limit", default=10)
    return parser

if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
