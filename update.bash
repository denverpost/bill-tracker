#!/bin/bash
# Update the data, update the site, FTP it.

# See if the data has changed since the last time we checked.
# The latest timestamp's on the site is saved in a file called... log_timestamp.
LATEST=`cat log_timestamp`
# The current timestamp of Sunlight data is gathered here:
CURRENT=`python legquery.py --updated`
touch RUNNING

if [ "$LATEST" = "$CURRENT" ]; then rm RUNNING; exit 0; fi

echo $CURRENT > log_timestamp
echo $CURRENT >> log_update

# Update the data
python legquery.py --session 2016a --details
python legquery.py

# Update the site and FTP it.
python deploy.py --news
python deploy.py --freeze --ftp --session 2016a
rm RUNNING
