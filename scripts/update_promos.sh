#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_update_promos.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_update_promos.sh

cd ~/sciteit/r2
/usr/local/bin/paster run run.ini -c "from r2.lib import promote; promote.Run()">>/home/sciteit/sciteit/scripts/RUN_update_promos.sh
