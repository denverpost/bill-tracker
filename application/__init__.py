#!/usr/bin/env python
import os
from flask import Flask
from flask import Markup
from flask_flatpages import FlatPages

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
with app.app_context():
    app.page = page
    app.sessions = ['2011a', '2012a', '2012b', '2013a', '2014a', '2015a'] #***HC
    app.session = ['2015a'] #***HC CURRENT SESSION

import application.flatpage
import application.bills
