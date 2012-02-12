#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_reindex_all.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_reindex_all.sh

cd ~/sciteit/r2
/home/sciteit/sciteit/scripts/saferun.sh /tmp/share.pid /usr/local/bin/paster run run.ini r2/lib/solrsearch.py -c "reindex_all()">>/home/sciteit/sciteit/scripts/RUN_reindex_all.sh
