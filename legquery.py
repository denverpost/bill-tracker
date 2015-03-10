#!/usr/bin/env python
import sunlight
import json
import os

class Sunlight:
	def __init__(self):
        self.alert='hey'
	def get_bill_list(self):
        pass
	def get_bill_detail(self):
        pass

def main():
    co_bill = sunlight.openstates.bills(state='co')
    # print json.dumps(co_bill)
    fh = open('co-bills.json', 'wb')
    json.dump(co_bill, fh)
    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/output' % directory):
        os.mkdir('%s/output' % directory)

if __name__ == '__main__':
	main()
