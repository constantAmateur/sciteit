#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_update_sr_names.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_update_sr_names.sh

cd ~/sciteit/r2
~/sciteit/scripts/saferun.sh /tmp/update_sr_names.pid nice /usr/local/bin/paster --plugin=r2 run run.ini r2/lib/subsciteit_search.py -c "load_all_sciteits()">>/home/sciteit/sciteit/scripts/RUN_update_sr_names.sh
