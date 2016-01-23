#!/bin/bash
# ftp flat files to prod.
# Assumes a virtualenv named BILL, as well as virtualenvwrapper.
# pip install virtualenv; pip install virtualenvwrapper
# Also assumes env vars REMOTE_DIR and REMOTE_HOST:
# export REMOTE_DIR='path/on/remote/server/to/publish'; export REMOTE_HOST='ftp.servername.com'

ENVIRON='PROD'

source /usr/local/bin/virtualenvwrapper.sh
workon BILL

export environ=$ENVIRON
python freeze.py
#mv application/build application/public
#scp -r application/public $DEST
./ftp.bash --dir $REMOTE_DIR --source_dir application/build --host $REMOTE_HOST
#mv application/public application/build
export environ='DEV'

# FTP the data files
#./ftp.bash --dir $REMOTE_DIR/_input --host $REMOTE_HOST
# FTP the static files (should only update them when necessary.)
