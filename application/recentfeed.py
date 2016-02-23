#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Return recent items from a RSS feed. Recent means "In the last X days."
import os
import doctest
import json
import httplib2
import feedparser
import argparse
import types
from datetime import datetime, timedelta
from time import mktime

class RecentFeed:
    """ Methods for ingesting and publishing RSS feeds.
        >>> rf = RecentFeed()
        >>> rf.get('http://rss.denverpost.com/mngi/rss/CustomRssServlet/36/213601.xml')
        True
        >>> rf.parse()
        """

    def __init__(self, args={}):
        self.args = args
        if 'days' not in self.args:
            self.args['days'] = 0
        self.days = self.args['days']

    def get(self, url):
        """ Wrapper for API requests. Take a URL, return a json array.
            >>> url = 'http://rss.denverpost.com/mngi/rss/CustomRssServlet/36/213601.xml'
            >>> parser = build_parser()
            >>> args = parser.parse_args([url])
            >>> rf = RecentFeed(args)
            >>> rf.get(url)
            True
            >>> rf.parse()
            #>>> articles = rf.recently()
            """
        h = httplib2.Http('.tmp')
        (response, xml) = h.request(url, "GET")
        if response['status'] != '200':
            if 'verbose' in self.args and self.args.verbose:
                print "URL: %s" % url
            raise ValueError("URL %s response: %s" % (url, response.status))
        self.xml = xml
        return True

    def parse(self):
        """ Turn the xml into an object.
            """
        p = feedparser.parse(self.xml)
        self.p = p
        return p

    def recently(self):
        """ Return a feedparser entry object for the last X days of feed entries.
            """
        items = []
        for item in self.p.entries:
            dt = datetime.fromtimestamp(mktime(item.published_parsed))
            delta = datetime.today() - dt

            if delta.days > self.days:
                continue
            items.append(item)
            if 'verbose' in self.args and self.args['verbose']:
                print delta.days, dt
        self.items = items
        return items

def main(args):
    rf = RecentFeed(args)
    if args:
        articles = []
        for arg in args.urls[0]:
            if args.verbose:
                print arg
            rf.get(arg)
            rf.parse()
            articles.append(rf.recently())


        for article in articles[0]:
            if args.output == 'html':
                if type(article['title']) is types.UnicodeType:
                    article['title'] = article['title'].encode('utf-8', 'replace')
                print '<li><a href="{0}">{1}</a></li>'.format(article['id'], article['title'])
            elif args.output == 'json':
                json.dumps({'title': article['title'], 'url': article['id']})


def build_parser():
    """ We put the argparse in a method so we can test it
        outside of the command-line.
        """
    parser = argparse.ArgumentParser(usage='$ python recentfeed.py http://domain.com/rss/',
                                     description='''Takes a list of URLs passed as args.
                                                  Returns the items published today unless otherwise specified.''',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-d", "--days", dest="days", default=0, action="count")
    parser.add_argument("-o", "--output", dest="output", default="html", type=str)
    parser.add_argument("urls", action="append", nargs="*")
    return parser

if __name__ == '__main__':
    """ 
        """
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
