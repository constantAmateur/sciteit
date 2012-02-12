from r2.models import Subsciteit
from r2.lib.memoize import memoize
from r2.lib.db.operators import desc
from r2.lib import utils
from r2.lib.db import tdb_cassandra
from r2.lib.cache import CL_ONE

class SubsciteitsByPartialName(tdb_cassandra.View):
    _use_db = True
    _value_type = 'pickle'
    _use_new_ring = True
    _read_consistency_level = CL_ONE

def load_all_sciteits():
    query_cache = {}

    q = Subsciteit._query(Subsciteit.c.type == 'public',
                         Subsciteit.c._downs > 1,
                         sort = (desc('_downs'), desc('_ups')),
                         data = True)
    for sr in utils.fetch_things2(q):
        name = sr.name.lower()
        for i in xrange(len(name)):
            prefix = name[:i + 1]
            names = query_cache.setdefault(prefix, [])
            if len(names) < 10:
                names.append(sr.name)

    for name_prefix, subsciteits in query_cache.iteritems():
        SubsciteitsByPartialName._set_values(name_prefix, {'srs': subsciteits})

def search_sciteits(query):
    query = str(query.lower())

    try:
        result = SubsciteitsByPartialName._byID(query)
        return result.srs
    except tdb_cassandra.NotFound:
        return []

@memoize('popular_searches', time = 3600)
def popular_searches():
    top_sciteits = Subsciteit._query(Subsciteit.c.type == 'public',
                                   sort = desc('_downs'),
                                   limit = 100,
                                   data = True)
    top_searches = {}
    for sr in top_sciteits:
        name = sr.name.lower()
        for i in xrange(min(len(name), 3)):
            query = name[:i + 1]
            r = search_sciteits(query)
            top_searches[query] = r
    return top_searches

