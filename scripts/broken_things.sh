#!/bin/bash
touch /home/sciteit/scripts/RUN_broken_things.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_broken_things.sh

cd ~/sciteit/r2
/usr/local/bin/paster run run.ini r2/lib/utils/utils.py -c "find_recent_broken_things(from_time=timeago('3 minutes'), to_time=timeago('10 seconds'), delete=True)">>/home/sciteit/sciteit/scripts/RUN_broken_things.sh

