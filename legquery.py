#!/usr/bin/env python
import sunlight
import json
import os


if __name__ == '__main__':
    co_bill = sunlight.openstates.bills(state='co')
    # print json.dumps(co_bill)
    fh = open('co-bills.json', 'wb')
    json.dump(co_bill, fh)
    # We'll need to store the files we're writing somewhere, eventually.
    directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('%s/output' % directory):
        os.mkdir('%s/output' % directory)


