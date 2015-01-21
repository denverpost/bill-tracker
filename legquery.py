#!/usr/bin/env python
import sunlight
import json

if __name__ == '__main__':
	co_bill = sunlight.openstates.bills(state='co')
	# print json.dumps(co_bill)
	fh = open('co-bills.json', 'wb')
	json.dump(co_bill, fh)


