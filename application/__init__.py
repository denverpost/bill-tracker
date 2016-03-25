#!/usr/bin/env python
import os
from flask import Flask
from flask import Markup
from flask_flatpages import FlatPages
from datetime import date

app = Flask(__name__)
app.debug = True

# This dict is called on every .html document.
# We initialize it here in case all the fields aren't defined by the view method.
page = {
    'title': '',
    'url': '',
    'description': ''
}

pages = FlatPages(app)
# SITE CONFIG
with app.app_context():
    app.url_root = '/'
    app.page = page
    app.sessions = ['2011a', '2012a', '2012b', '2013a', '2014a', '2015a', '2016a'] #***HC
    app.session = '2016a' #***HC CURRENT SESSION
    # THE WEEK WE START PUBLISHING THE WEEK... need to figure out how we know when to end it.
    app.theweek = { '2016a': date(2016,2,20) }
    app.session_dates = { '2016a': [date(2016,1,13), date(2016,5,11)] }

import application.flatpage
import application.bills
