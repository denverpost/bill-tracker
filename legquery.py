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
        bill_details = sunlight.openstates.bill_detail(self.state, self.session, bill_id)
        fh = open('output/%s.json' % string.replace(bill_id, ' ', '_'), 'wb') 
        json.dump(bill_details, fh)
        return bill_details 


class BillTemplate(Template):

    def set_session(self, value):
        """ Set the object session value.
            """
        self.session = value
        return value

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
        elif self.data_type == 'bill_detail':
            output = self.write_bill_detail(output)

        # These replacements hold true for all templates
        #output = string.replace(output, '{{location}}', string.replace(self.location, '+', ' '))
        #output = string.replace(output, '{{slug}}', self.slug)

        page = self.read_file('html/base.html')
        template = string.replace(page, '{{content}}', output)
        template = string.replace(template, '{{url}}', string.replace(self.metadata['url'], '+', '_'))
        template = string.replace(template, '{{title}}', self.metadata['title'])
        template = string.replace(template, '{{description}}', self.metadata['description'])
        template = string.replace(template, '{{year}}', self.metadata['year'])
        template = string.replace(template, '{{month}}', self.metadata['month'].title())
        template = string.replace(template, '{{s}}', self.metadata['s'])
        template = string.replace(template, '{{breadcrumb_one}}', self.metadata['breadcrumb_one'])
        template = string.replace(template, '{{breadcrumb_two}}', self.metadata['breadcrumb_two'])
        template = string.replace(template, '{{breadcrumb_three}}', self.metadata['breadcrumb_three'])

        self.output = template
        return template

    def write_index(self, output):
        """ Handle writing the index page.
            """
        pass

    def write_bill_detail(self, output):
        """ Handle writing the bill detail page.
            """
        pass

    def write_file(self):
        """ Write the parsed contents of a template to a file.
            """
        self.slug = self.slug.replace('+', '_')
        self.slug = self.slug.replace(' ', '_')
        path = 'www/output/%s-%s.html' % ( self.data_type, self.slug )
        if self.session and self.session != '':
            path = 'www/output/%s/%s-%s.html' % ( self.session, self.data_type, self.slug )
        f = open(path, 'wb')
        f.write(self.output)
        f.close()
        return "Successfully written to %s" % path

def main():
    s = Sunlight()
    s.get_bill_list()

    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/www/output' % directory):
        os.mkdir('%s/www/output' % directory)
    session = s.get_session()
    if not os.path.isdir('%s/www/output/%s' % (directory, session)):
        os.mkdir('%s/www/output/%s' % (directory, session))

    bills = s.filter_bills_recent(1)
    for item in bills:
        details = s.get_bill_detail(item['bill_id'])
        t = BillTemplate(details, 'bill_detail')
        metadata = {
            's': '',
            'year': '',
            'months': '',
            'month': '',
            'days': '',
            'location': '',
            'url': 'http://extras.denverpost.com/app/bill-tracker/',
            'title': '',
            'breadcrumb_one': '',
            'breadcrumb_two': '',
            'breadcrumb_three': '',
            'description': ''
        }
        t.set_metadata(metadata)
        t.set_slug(item['bill_id'])
        t.set_session(session)
        t.write_template()
        t.write_file()
        


if __name__ == '__main__':
	main()
