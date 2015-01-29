#!/bin/bash
# Publish these files.
# Assumes a virtualenv named BILL, as well as virtualenvwrapper.
# pip install virtualenv; pip install virtualenvwrapper
# Also assumes env vars REMOTE_DIR and REMOTE_HOST:
# export REMOTE_DIR='path/on/remote/server/to/publish'; export REMOTE_HOST='ftp.servername.com'

source /usr/local/bin/virtualenvwrapper.sh
workon BILL

# Write the flat files
python spreadsheet.py City="$CITY"

# FTP the data files
./ftp.bash --dir $REMOTE_DIR/output --host $REMOTE_HOST
# FTP the static files (should only update them when necessary.)
./ftp.bash --dir $REMOTE_DIR --source_dir www --host $REMOTE_HOST
