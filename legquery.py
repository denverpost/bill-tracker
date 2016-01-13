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
        self.session = self.bills[0]['session']
        fh = open('co-bills.json', 'wb')
        json.dump(self.co_bill, fh)
        return True

    def filter_bills_recent(self, limit = 10):
        """ Filter recent bills.
            """
        return self.bills[:limit]
 
    def get_bill_detail(self, bill_id):
        """ Get bill details for a single bill.
            """
        bill_details = sunlight.openstates.bill_detail(self.state, self.session, bill_id)
        print bill_details 
        fh = open('output/%s.json' % string.replace(bill_id, ' ', '_'), 'wb') 
        json.dump(bill_details, fh)
        return bill_details 


class BillTemplate(Template):

    def write_template(self):
        """ Doco
            """
        pass

def main():
    s = Sunlight()
    s.get_bill_list()
    bills = s.filter_bills_recent()
    for item in bills:
        details = s.get_bill_detail(item['bill_id'])
    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/output' % directory):
        os.mkdir('%s/output' % directory)

if __name__ == '__main__':
	main()
