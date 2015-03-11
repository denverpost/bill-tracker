#!/usr/bin/env python
import sunlight
import json
import os
import string

class Sunlight:
    def __init__(self):
        self.alert='hey'
    def get_bill_list(self):
        """ Get list of bills. """
        co_bill = sunlight.openstates.bills(state='co')
        fh = open('co-bills.json', 'wb')
        json.dump(co_bill, fh)
        return True

    def get_bill_detail(self, bill_id):
        """ Get bill details for a single bill. """
        bill_details = sunlight.openstates.bill_detail('co', self.session, bill_id)
        print bill_details 
        details_fh = open('output/%s.json' % string.replace(bill_id, ' ', '_'), 'wb') 
        json.dump(item, details_fh)
        return True

def main():
    s = Sunlight()
    #fh = open('co-bills.json', 'rb')
    #co_bill = json.load(fh)
    #for item in co_bill:
    #json.dump(co_bill, fh)
    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/output' % directory):
        os.mkdir('%s/output' % directory)

if __name__ == '__main__':
	main()
