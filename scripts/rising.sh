#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_rising.sh
echo `date`>> /home/sciteit/sciteit/scripts/RUN_rising.sh

cd ~/sciteit/r2
/home/sciteit/sciteit/scripts/saferun.sh /tmp/rising.pid /usr/local/bin/paster run run.ini r2/lib/rising.py -c "set_rising()">>/home/sciteit/sciteit/scripts/RUN_rising.sh
