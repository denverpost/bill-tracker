#!/usr/bin/env python
import sunlight
import json
import doctest
import os, sys
import string
import argparse
import httplib2
import types

class Sunlight:

    def __init__(self, args={}):
        """ Initialize the object.
            >>> s = Sunlight()
            """
        self.state='co'
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.bills = []
        self.args = args

    def get_bill_list(self, session=None):
        """ Get list of bills, sometimes from a particular session.
            >>> s = Sunlight()
            >>> s.get_bill_list('2016a')
            Session: 2016a
            True
            """
        if session:
            bills = sunlight.openstates.bills(state=self.state, session=session.upper())
            # Because querying Sunight's API like that ^ returns all bills,
            # not just the ones from the specified session.
            for item in bills:
                if item['session'] == session.upper():
                    self.bills.append(item)
            filename = '_input/%s-bills-%s.json' % (self.state, session.lower())
        else:
            self.bills = sunlight.openstates.bills(state=self.state)
            filename = '_input/%s-bills.json' % (self.state)

        self.session = self.bills[0]['session'].lower()
        if 'updated' not in self.args:
            print "Session: %s" % self.session
        fh = open(filename, 'wb')
        json.dump(self.bills, fh)
        return True

    def filter_bills_recent(self, limit = 10):
        """ Filter recent bills.
            >>> s = Sunlight()
            >>> s.get_bill_list()
            Session: 2016a
            True
            >>> print len(s.filter_bills_recent(1))
            1
            """
        if limit == 0:
            return self.bills
        return self.bills[:limit]
 
    def get_bill_detail(self, bill_id):
        """ Get bill details for a single bill.
            >>> s = Sunlight()
            >>> s.get_bill_list('2011a')
            Session: 2011a
            True
            >>> bill_detail = s.get_bill_detail(s.bills[0]['bill_id'])
            >>> print bill_detail['bill_id']
            SB 11-173
            """
        bill_slug = string.replace(bill_id.lower(), ' ', '_')
        if not os.path.isdir('%s/_input/%s' % (self.directory, self.session)):
            os.mkdir('%s/_input/%s' % (self.directory, self.session))
        bill_details = sunlight.openstates.bill_detail(self.state, self.session.upper(), bill_id)
        fh = open('_input/%s/%s.json' % (self.session, bill_slug), 'wb')
        json.dump(bill_details, fh)

        #self.get_bill_pdf(bill_slug, bill_details)
        return bill_details 

    def get_bill_pdf(self, bill_slug, details):
        """ Request and save the current version of the bill's PDF.
            """
        h = httplib2.Http('')
        #print details['versions'][0]['url']
        #print details['versions']
        response, content = h.request(details['versions'][0]['url'], 'GET', headers={}, body='')
        if response.status > 299:
            print 'ERROR: HTTP response %s' % response.status
            return False
        fn = open('_input/%s/%s.pdf' % (self.session, bill_slug), 'wb')
        fn.write(content)
        fn.close
        return True


def main(args):
    """ Example usage:
        This  update this session's bill details with the latest data,
        and then builds the full index of all sessions / bills.
        $ python legquery.py --session 2016a --details
        $ python legquery.py
        """

    s = Sunlight(args)
    s.get_bill_list(args.session)

    if 'updated' in args and args.updated:
        print s.bills[0]['updated_at']
        return False

    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/_input' % directory):
        os.mkdir('%s/_input' % directory)

    # Get all the bills if we're doing by session
    if args.session:
        bills = s.bills
    else:
        bills = s.filter_bills_recent(int(args.limit))

    if args.details:
        i = 0
        if args.verbose:
            print "Downloading bill details for %d bills" % len(bills)
        for item in bills:
            i += 1
            if args.verbose:
                print i, item['bill_id']
            try:
                details = s.get_bill_detail(item['bill_id'])
            except:
                if args.verbose:
                    print item['session']
                s.session = item['session'].lower()
                details = s.get_bill_detail(item['bill_id'])



def build_parser(args):
    """ This method allows us to test the args.
        >>> parser = build_parser(['-v'])
        >>> print args.verbose
        True
        """
    parser = argparse.ArgumentParser(usage='$ python legquery.py',
                                     description='Download data from Sunlight and update bill indexes.',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true",
                        help="Run doctests, display more info.")
    parser.add_argument("-u", "--updated", dest="updated", default=False, action="store_true",
                        help="Returns nothing but the last-updated timestamp from the latest bill.")
    parser.add_argument("-d", "--details", dest="details", default=False, action="store_true",
                        help="Also query and download the details for each bill. This includes PDFs.")
    parser.add_argument("-s", "--session", dest="session",
                        help="Query only one session, i.e. 2016a, 2015a, 2014a etc.")
    parser.add_argument("-l", "--limit", dest="limit", default=0,
                        help="Truncate the number of bills we handle. Ignored if a session param is passed.")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
