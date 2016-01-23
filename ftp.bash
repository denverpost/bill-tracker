#!/bin/bash
# ftp files from one directory to another.
# Assumes credentials are stored in a file in the home directory named .ftppass
# The password and username can be set in the environment (export FTP_PASS='pass')
# Alternately, the password can be stored is a file in the user's root dir, named .ftp_pass.
#
# Example usage:
# ./ftp.bash --dir /path/to/where/you/want/the/files --host ftp.domain.com
#
# NOTE: FTP IS AN INSECURE PROTOCOL AND SHOULD BE AVOIDED.

SOURCE_DIR='output'
DIR=''
HOST=''
if [ -z "$FTP_USER" ]; then FTP_USER=''; fi
if [ -z "$FTP_PASS" ]; then FTP_PASS=`cat ~/.ftp_pass`; fi
FILES='*'
while [ "$1" != "" ]; do
    case $1 in
        -d | --dir ) shift
            DIR=$1
            ;;
        -s | --source_dir ) shift
            SOURCE_DIR=$1
            ;;
        -h | --host ) shift
            HOST=$1
            ;;
        -u | --user ) shift
            FTP_USER=$1
            ;;
        -f | --files ) shift
            FILES=$1
            ;;
    esac
    shift
done

echo $SOURCE_DIR
cd $SOURCE_DIR
ftp -v -n $HOST << EOF
user $FTP_USER $FTP_PASS
cd $DIR
bin
passive
prompt
mput $FILES
bye                                                                                                                                                                          
EOF
