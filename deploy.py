#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Move files to production
import argparse
import string
import os, sys
from FtpWrapper import FtpWrapper
import freeze


if __name__ == '__main__':
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
