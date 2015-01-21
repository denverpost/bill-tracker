#!/usr/bin/env python
import sunlight
import json

if __name__ == '__main__':
	co_bill = sunlight.openstates.bills(state='co')
	json.dumps(co_bill)

