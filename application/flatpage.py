#!/usr/bin/env python
from flask import render_template, url_for, redirect, abort, request
from flask.views import View
import inspect
from application import app
from application import pages
from werkzeug.contrib.atom import AtomFeed
from datetime import datetime


class FlatPageView(View):
    """ There was lots of repetitive code in this flatpage file, and now there's not.
        """

    def __init__(self, page_name):
        self.page_name = page_name

    def get_template(self):
        return self.page.meta.get('template', 'flatpage.html')

    def render_template(self, context):
        return render_template(self.get_template(), **context)

    def dispatch_request(self):
        app.page['title'] = ''
        app.page['description'] = ''
        response = {
            app: app
        }
        self.page = pages.get_or_404(self.page_name)
        context = { 'response': response, 'page': self.page }
        return self.render_template(context)

#app.add_url_rule('/about/updates/', view_func=FlatPageView.as_view('update', page_name='update'))
app.add_url_rule('/about/', view_func=FlatPageView.as_view('about', page_name='about'))
#app.add_url_rule('/about/notifications/', view_func=FlatPageView.as_view('notifications', page_name='notifications'))
#app.add_url_rule('/about/notifications/unsubscribe/', view_func=FlatPageView.as_view('unsubscribe', page_name='unsubscribe'))
#app.add_url_rule('', view_func=FlatPageView.as_view('', page_name=''))

"""
@app.route('/feeds/recent.atom')
def recent_feed():
    feed = AtomFeed('Colorado Bill Tracker: Recent',
                    feed_url=request.url, url=request.url_root)
    feed.add('Crime Data updated', '',
             content_type='html',
             url='http://denvercrimes.com/',
             updated=datetime.today(),
             published=datetime.today())
    return feed.get_response()

@app.route('/site-map/')
def sitemap():
    response = {
        'dicts': app.dicts,
        'app': app
    }
    return render_template('sitemap.html', response=response)
"""
