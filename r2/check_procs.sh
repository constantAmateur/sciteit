#!/bin/sh

cd /home/ri/sciteit/r2
/usr/bin/paster run local.ini supervise_watcher.py -c "Alert(restart_list=['MEM'])"
