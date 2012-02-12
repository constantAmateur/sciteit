from pylons import g

from r2.lib.memoize import memoize
from r2.lib import _normalized_hot
from r2.models import Subsciteit

from r2.lib._normalized_hot import get_hot, _expand_children, _expand_children_byID # pull this into our namespace

@memoize('normalize_hot', time = g.page_cache_time)
def normalized_hot_cached(sr_ids):
    return _normalized_hot.normalized_hot_cached(sr_ids)

def l(li):
    if isinstance(li, list):
        return li
    else:
        return list(li)

def normalized_hot(sr_ids):
    sr_ids = l(sorted(sr_ids))
    print "The ids"
    print sr_ids
    return normalized_hot_cached(sr_ids) if sr_ids else ()

def expand_children(srs,byID=False):
    print "Expanding %s" % srs
    if byID:
        ret = _expand_children_byID(srs if isinstance(srs,list) else [srs])
    else:
        ret = _expand_children(srs if isinstance(srs,list) else [srs])
    #Efficient way of making unique
    ret = list(set(ret))
    print "Got %s" % ret
    return ret

