#!/bin/bash
touch /home/sciteit/sciteit/scripts/RUN_send_mail.sh
echo `date`>>/home/sciteit/sciteit/scripts/RUN_send_mail.sh

cd ~/sciteit/r2
/home/sciteit/sciteit/scripts/saferun.sh /tmp/share.pid /usr/local/bin/paster run run.ini r2/lib/emailer.py -c "send_queued_mail()">>/home/sciteit/sciteit/scripts/RUN_send_mail.sh
