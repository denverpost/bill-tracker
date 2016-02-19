#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Move files to production
import argparse
import string
import os, sys
import doctest
import httplib2
from FtpWrapper import FtpWrapper
import freeze

current_session = '2016a' #HARD-CODED HC

def main(args):
    """ Turn every URL into flatfile, ftp it to prod.
        >>> args = build_parser(['--verbose'])
        >>> main(args)
        False
        """
    if args.do_freeze:
        freeze.freezer.freeze()
    if not args.do_ftp:
        return False

    basedir = 'application/build/'
    os.chdir(basedir)
    ftp_path = '/DenverPost/app/bill-tracker/'
    ftp_config = {
        'user': os.environ.get('FTP_USER'),
        'host': os.environ.get('FTP_HOST'),
        'port': os.environ.get('FTP_PORT'),
        'upload_dir': ftp_path
    }
    if args.verbose:
        print ftp_config

    ftp = FtpWrapper(**ftp_config)

    # Always FTP the homepage.
    ftp.send_file('index.html', '.')

    for dirname, dirnames, filenames in os.walk('.'):

        # Sometimes we only want to upload files for a particular session.
        # The dirname, dirnames in this loop looks like:
        # . ['bills'] <-- on the top level, "." is dirname and the list is the dirnames.
        # ./bills ['2011a', '2012a', '2012b', '2013a', '2014a', '2015a', '2016a'] <-- the next level down
        # ./bills/2011a ['hb_11-1001', 'hb_11-1002'... <-- the next down from that
        if args.session:
            if 'bills/' in dirname:
                if args.session not in dirname:
                    continue

        if args.no_session:
            if '201' in dirname:
                continue
            else:
                print dirname, dirnames

        for subdirname in dirnames:
            if args.verbose:
                print dirname, subdirname

            # Skip the endless directory creation on previous years.
            if current_session not in dirname:
                if args.verbose:
                    print "SKIPPING mkdir on %s" % subdirname
                continue
            ftp.mkdir(os.path.join(dirname, subdirname))

        for filename in filenames:
            if args.verbose:
                print(os.path.join(dirname, filename))
            try:
                ftp.send_file(os.path.join(dirname, filename), dirname)
            except:
                print "ERROR: Could not upload", 
                print(os.path.join(dirname, filename))

            # Bust the cache on extras
            h = httplib2.Http('')
            url = '%s/' % dirname
            url = string.replace(url, '//', '/')
            url = string.replace(url, '.', 'http://extras.denverpost.com/app/bill-tracker', 1)
            if args.verbose:
                print "PURGE:", url
            try:
                response, content = h.request('%s/' % url, 'PURGE', headers={}, body='')
            except:
                print "ERROR: Could not bust cache on %s" % url

    ftp.disconnect()
    return True

def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print args.verbose
        True
        """
    parser = argparse.ArgumentParser(usage='$ python deploy.py',
                                     description='Deploy billtracker to production.',
                                     epilog='Examply use: python deploy.py --ftp --freeze --session 2016a')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("--freeze", dest="do_freeze", default=False, action="store_true",
                        help="Take a snaphot of the site before uploading.")
    parser.add_argument("--ftp", dest="do_ftp", default=False, action="store_true",
                        help="FTP the site to the production server.")
    parser.add_argument("--nosession", dest="no_session", default=False, action="store_true",
                        help="Only upload basic indexes & homepage.")
    parser.add_argument("-s", "--session", dest="session", default=False)
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
