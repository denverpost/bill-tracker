#!/usr/bin/env python
import os
from flask import Flask
from flask import Markup
from flask_flatpages import FlatPages

app = Flask(__name__)
app.debug = True

page = {
    'title': '',
    'url': '',
    'description': ''
}

pages = FlatPages(app)
with app.app_context():
    app.page = page
    app.sessions = ['2015A']

import application.flatpage
import application.bills
