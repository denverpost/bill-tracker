#!/bin/bash
# Update the data, update the site, FTP it.

# See if the data has changed since the last time we checked.
# The latest timestamp's on the site is saved in a file called... log_timestamp.
LATEST=`cat log_timestamp`
# The current timestamp of Sunlight data is gathered here:
CURRENT=`python legquery.py --updated`

if [ "$LATEST" -eq "$CURRENT" ]; then exit 0; fi

echo $CURRENT > log_timestamp
echo $CURRENT >> log_update
