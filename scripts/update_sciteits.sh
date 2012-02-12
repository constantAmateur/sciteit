#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_update_sciteits.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_update_sciteits.sh

cd ~/sciteit/r2
/home/sciteit/sciteit/scripts/saferun.sh /tmp/updatesciteits.pid nice /usr/local/bin/paster --plugin=r2 run run.ini r2/lib/sr_pops.py -c "run()">>/home/sciteit/sciteit/scripts/RUN_update_sciteits.sh
