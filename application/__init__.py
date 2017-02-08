#!/usr/bin/env python
import os
import json
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
# Most of these vars are used on the site in some way.
# We store them here and then pass them to the template (you see them as response.app....)
with app.app_context():
    app.url_root = '/'
    app.page = page
    app.sessions = ['2011a', '2012a', '2012b', '2013a', '2014a', '2015a', '2016a', '2017a'] #***HC - append the next session
    app.session = '2017a' #***HC CURRENT SESSION - replace with the next session
    # THE WEEK WE START PUBLISHING THE WEEK... need to figure out how we know when to end it.
    app.theweek = { 
        '2017a': date(2017,2,6),
        '2016a': date(2016,2,20) } #***HC - append
    app.session_dates = { 
        '2017a': [date(2017,1,13), date(2017,5,11)],
        '2016a': [date(2016,1,13), date(2016,5,11)] } #***HC - append
    try:
        days = json.load(open('_input/days_%s.json' % app.session))
        weeks = json.load(open('_input/weeks_%s.json' % app.session))
        app.recent = {
                        'week': weeks[-1],
                        'day': days[-1]
                     }                   
    except:
        app.recent = {
                        'week': '',
                        'day': ''
                     }                   

import application.flatpage
import application.bills
