#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_update_rss.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_update_rss.sh

cd ~/sciteit/r2
/usr/local/bin/paster run run.ini r2/lib/sr_rss.py -c "run()"
#>>/home/sciteit/sciteit/scripts/RUN_update_rss.sh
