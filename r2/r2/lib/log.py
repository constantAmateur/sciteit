# The contents of this file are subject to the Common Public Attribution
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
# All portions of the code written by CondeNet are Copyright (c) 2006-2010
# CondeNet, Inc. All Rights Reserved.
################################################################################

from pylons import g
from r2.lib import amqp
from datetime import datetime
import cPickle as pickle
import traceback

tz = g.display_tz

Q = 'log_q'

def _default_dict():
    return dict(time=datetime.now(tz),
                host=g.sciteit_host,
                port="default",
                pid=g.sciteit_pid)

# e_value and e should actually be the same thing.
# e_type is the just the type of e_value
# So e and e_traceback are the interesting ones.
def log_exception(e, e_type, e_value, e_traceback):
    d = _default_dict()

    d['type'] = 'exception'
    d['traceback'] = traceback.extract_tb(e_traceback)

    d['exception_type'] = e.__class__.__name__
    s = str(e)
    d['exception_desc'] = s[:10000]

    amqp.add_item(Q, pickle.dumps(d))

def log_text(classification, text=None, level="info"):
    from r2.lib.filters import _force_utf8
    if text is None:
        text = classification

    if level not in ('debug', 'info', 'warning', 'error'):
        print "What kind of loglevel is %s supposed to be?" % level
        level = 'error'

    d = _default_dict()
    d['type'] = 'text'
    d['level'] = level
    d['text'] = _force_utf8(text)
    d['classification'] = classification

    amqp.add_item(Q, pickle.dumps(d))
