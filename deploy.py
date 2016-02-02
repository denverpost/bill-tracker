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
        """
    if args.do_freeze:
        freeze.freezer.freeze()

    basedir = 'application/build/'
    os.chdir(basedir)
    ftp_path = '/DenverPost/app/bill-tracker/'
    ftp_config = {
        'user': os.environ.get('FTP_USER'),
        'host': os.environ.get('FTP_HOST'),
        'port': os.environ.get('FTP_PORT'),
        'upload_dir': ftp_path
    }
    ftp = FtpWrapper(**ftp_config)

    for dirname, dirnames, filenames in os.walk('.'):
        for subdirname in dirnames:
            ftp.mkdir(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for filename in filenames:
            print(os.path.join(dirname, filename))
            ftp.send_file(os.path.join(dirname, filename))

    ftp.disconnect()
    return True

def build_parser(args):
    """ This method allows us to test the args.
        >>> parser = build_parser()
        >>> print args
        """
    parser = argparse.ArgumentParser(usage='$ python deploy.py',
                                     description='Deploy billtracker to production',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-f", "--freeze", dest="do_freeze", default=False, action="store_true")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
