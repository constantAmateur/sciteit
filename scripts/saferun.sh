#!/bin/bash

# "The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.sciteit.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
# 
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
# 
# The Original Code is Sciteit.
# 
# The Original Developer is the Initial Developer.  The Initial Developer of the
# Original Code is CondeNet, Inc.
# 
# All portions of the code written by CondeNet are Copyright (c) 2006-2009
# CondeNet, Inc. All Rights Reserved.
################################################################################


if [ $# -lt 2 ]; then
    echo "usage: $0 [pidfile] [command]" 1>&2
    exit 1
fi

PIDFILE=$1
shift 1
COMMAND=$1
shift 1

#check pid file for process
if [ -a $PIDFILE ]; then
    c=$(ps -p $(cat $PIDFILE) | wc -l)
    if [ $c -eq 2 ]; then
        echo 'already running' 1>&2
        ls -l $PIDFILE 1>&2
        exit 1
    fi
fi

#dump pid
echo "$$" > $PIDFILE

#run command
$COMMAND "$@"

#remove pid file
rm $PIDFILE
