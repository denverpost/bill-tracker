#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Move files to production
import argparse
import string
import os, sys
import doctest
from FtpWrapper import FtpWrapper
import freeze

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

        for subdirname in dirnames:
            if args.verbose:
                print dirname, subdirname
            ftp.mkdir(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for filename in filenames:
            if args.verbose:
                print(os.path.join(dirname, filename))
            ftp.send_file(os.path.join(dirname, filename))

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
    parser.add_argument("--freeze", dest="do_freeze", default=False, action="store_true")
    parser.add_argument("--ftp", dest="do_ftp", default=False, action="store_true")
    parser.add_argument("-s", "--session", dest="session", default=False)
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
