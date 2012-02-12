from sciteit_base import SciteitController
from validator import *
from r2.lib.db.queries import CachedResults

import cPickle as pickle
from urllib import unquote

class QueryController(SciteitController):
    @validate(query = nop('query'))
    def POST_doquery(self, query):
        if g.enable_doquery:
            cr = pickle.loads(query)
            cr.update()
        else:
            abort(403, 'forbidden')
