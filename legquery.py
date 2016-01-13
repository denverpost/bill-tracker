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
        print "Session: %s" % self.session
        fh = open('%s-bills.json' % self.state, 'wb')
        json.dump(self.bills, fh)
        return True

    def filter_bills_recent(self, limit = 10):
        """ Filter recent bills.
            """
        return self.bills[:limit]
 
    def get_bill_detail(self, bill_id):
        """ Get bill details for a single bill.
            """
        bill_details = sunlight.openstates.bill_detail(self.state, self.session, bill_id)
        fh = open('output/%s.json' % string.replace(bill_id, ' ', '_'), 'wb') 
        json.dump(bill_details, fh)
        return bill_details 


class BillTemplate(Template):

    def write_template(self):
        """ The search-and-replaces specific to the legislative bill templates.
            Inherits basic class methods from template.py.
            """
        # The template is loaded in the init method.
        if self.template == '':
            raise ValueError("template var must exist and be something.")
        output = self.template

        if self.data_type == 'index':
            output = self.write_index(output)
        elif self.data_type == 'detail':
            output = self.write_detail(output)

        # These replacements hold true for all templates
        #output = string.replace(output, '{{location}}', string.replace(self.location, '+', ' '))
        #output = string.replace(output, '{{slug}}', self.slug)

        self.output = output
        return output

    def write_index(self, output):
        """ Handle writing the index page.
            """
        pass

    def write_detail(self, output):
        """ Handle writing the bill detail page.
            """
        pass

def main():
    s = Sunlight()
    s.get_bill_list()
    bills = s.filter_bills_recent(1)
    for item in bills:
        details = s.get_bill_detail(item['bill_id'])
        t = BillTemplate(details, 'bill_detail')
        t.set_slug(item['bill_id'])
        t.write_template()
        t.write_file()
        
    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/output' % directory):
        os.mkdir('%s/output' % directory)

if __name__ == '__main__':
	main()
