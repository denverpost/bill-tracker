#!/bin/bash
# Update the data, update the site, FTP it.

# See if the data has changed since the last time we checked.
# The latest timestamp's on the site is saved in a file called... log_timestamp.
source /usr/local/bin/virtualenvwrapper.sh
workon BILL
LATEST=`cat log_timestamp`
# The current timestamp of Sunlight data is gathered here:
CURRENT=`python legquery.py --updated`
touch RUNNING
TEST=0
while [ "$1" != "" ]; do
    case $1 in
        -t | --test ) shift
            TEST=1
            ;;
    esac
    shift
done

if [ "$LATEST" = "$CURRENT" ]; then rm RUNNING; exit 0; fi

echo $CURRENT > log_timestamp
echo $CURRENT `date` >> log_update

# Update the data
python legquery.py --session 2016a --details
python legquery.py

# Update the site's flat files
python deploy.py --news
python deploy.py --freeze

# FTP it if we're not testing it.
if [ $TEST == 0 ]; then
    python deploy.py --ftp --nosession
    python deploy.py --ftp --session 2016a
fi

rm RUNNING
