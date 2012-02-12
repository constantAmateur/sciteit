#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_index_changed.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_index_changed.sh

cd ~/sciteit/r2
/home/sciteit/sciteit/scripts/saferun.sh /tmp/index_changed.pid /usr/local/bin/paster run run.ini r2/lib/solrsearch.py -c "run_changed()">>/home/sciteit/sciteit/scripts/RUN_index_changed.sh
