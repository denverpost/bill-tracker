#!/usr/bin/env python
# FTP files with python.
import os
from ftplib import FTP

class FtpWrapper():
    """ class ftpWrapper handles FTP operations. 
        Assumes the password is stored in an env var named FTP_PASS
        Currently this works best for uploading one or two files. Needs to be
        built out if it's going to handle large numbers of file uploads. 
        """

    def __init__(self, **config):
        """ config should look something like this:
            config = {
                'user': username,
                'host': host,
                'port': 21,
                'upload_dir': path
            }
            """
        self.config = config
        self.password = os.environ.get('FTP_PASS').strip()
        self.connect()

    def ftp_callback(self, data):
        print
        print
        print
        print ''
 
    def connect(self):
        """ Connect to a server.
            """
        self.ftp = FTP(self.config['host'], self.config['user'], self.password)
        return True

    def disconnect(self):
        """ Disconnect from a server.
            """
        self.ftp.close()
        return True

    def mkdir(self, path=None):
        """ Create a string of directories, if the dirs don't already exist.
            """
        if path is None:
            path = self.config['upload_dir']

        for item in path.split('/'):
            if item == '':
                continue
            print self.ftp.pwd()
            try:
                self.ftp.cwd('./%s' % item)
            except:
                self.ftp.mkd('./%s' % item)
                self.ftp.cwd('./%s' % item)
        return True

    def send_file(self, fp):
        """ Open a connection, read a file, upload that file.
            Requires the filename.
            """
        if self.ftp is None:
            self.connect()

        file_h = open(fp, 'r')
        #blocksize = len(file_h.read())
        blocksize = 4096
        fn = fp.split('/')[-1]

        self.ftp.cwd(self.config['upload_dir'])
        try:
            self.ftp.storbinary('STOR %s' % fn, file_h, blocksize, self.ftp_callback)
            print 'SUCCESS: FTP\'d %s to %s' % (fn, self.config['host'])
        except:
            print 'ERROR: Could not FTP-->STOR %s' % fn
        file_h.close
