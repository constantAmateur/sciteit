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
from r2.lib.db.thing import NotFound
from r2.lib.db import tdb_cassandra
from r2.models import Subsciteit,Account,Link,LinksByUrl,NotFound
from r2.lib.utils import get_sr_rss,build_sr_tree
from r2.lib.utils import unicode_safe
from r2.lib.db import queries
from r2.lib.db.queries import changed
from r2.lib.utils import sanitize_url
from r2.lib.utils import domain
from time import sleep
from pylons import g
import re, feedparser,urllib2,random

NEVER = 'Thu, 31 Dec 2037 23:59:59 GMT'
MAX_TITLE_LENGTH=300
DOMAIN_WHITELIST=['arxiv.org','feeds.nature.com']

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

def link_equals(urla,urlb,fast=False):
    try:
        if not fast:
	    urla=urllib2.urlopen(HeadRequest(urla)).geturl()
            urlb=urllib2.urlopen(HeadRequest(urlb)).geturl()
	urla=sanitize_url(urla)
	urlb=sanitize_url(urlb)
	return urla==urlb
    except:
        pass
    return False

def find_dups(new,fast=True):
    """Check to see if anyone else is using the same feed...  If they are return the category, if not return none"""
    rss = get_sr_rss()
    new = sanitize_url(new)
    for k in [k for k in rss.keys() if rss[k]]:
        print rss[k]
        if link_equals(rss[k],new,fast=fast):
	    return k
    return None

def run():
    #rss = get_sr_rss()
    #names = rss.keys()
    #Build tree order, this will be from root to leaves.
    order=build_sr_tree(Subsciteit._by_name(g.default_sr)._id)
    #Populate RSS in the other order...
    order.reverse()
    for sr_id in order:
        sr = Subsciteit._byID(sr_id)
	if sr.rss_source:
	    #ac=Account._byID(srob.moderators[0])
	    ac=Account._by_name(g.system_user)
            print "Populating %s as %s using feed |%s|" % (sr.name,ac.name,sr.rss_source)
            submit_rss_links(sr.name,sr.rss_source,user=ac._id)

def fetch_feed(rss):
    if rss:
        rss=sanitize_url(rss)
        if rss:
	    try:
	        return feedparser.parse(rss)
	    except:
	        pass
    print "Invalid feed."
    return None


def fetch_article(article,titlefield,linkfield,niceify=False):
    if isinstance(article,dict):
        keys=article.keys()
	if titlefield in keys and linkfield in keys:
	    title=unicode_safe(validate_title(article[titlefield]))
	    link=validate_link(article[linkfield])
	    if niceify:
	        title=niceify_title(title,niceify)
		print "Niced title: %s" % title
	    if title and link:
	        return dict(title=title,link=link)
    return None

def validate_title(title):
    only_whitespace = re.compile(r"\A\s*\Z", re.UNICODE)
    text = title or ''
    if not text or only_whitespace.match(text):
        print "Invalid Title: %s" % text
        return False
    if len(text)>MAX_TITLE_LENGTH:
        return text[:MAX_TITLE_LENGTH]
    return text

def niceify_title(title,redict):
    return re.sub(redict['find'],redict['replace'],title)

def validate_link(url,whitelist=False):
    if url:
        url=sanitize_url(url)
        if url:
	    if whitelist and domain(url) not in DOMAIN_WHITELIST:
	        print "Domain %s not in whitelist." % domain(url)
		return False
            try:
                lbu = LinksByUrl._byID(LinksByUrl._key_from_url(url))
            except tdb_cassandra.NotFound:
                return url
            link_id36s = lbu._values()
	    links = Link._byID36(link_id36s, data=True, return_dict=False)
	    links = [l for l in links if not l._deleted]
	    if len(links)==0:
	        return url
	    print "Link %s exists..." % url
    return False 

def submit_rss_links(srname,rss,user,titlefield='title',linkfield='link'):
    #Fuck the API, let's just do it the way we would if we were really doing it.  This avoids screwing around with cookies and so forth...
    feed=fetch_feed(rss)
    if feed is None:
        return
    ac=Account._byID(user)
    sr=Subsciteit._by_name(srname)
    ip='0.0.0.0'
    niceify=False
    if domain(rss)=="arxiv.org":
        niceify=dict(find="\(arXiv:.*?\)",replace="")
    #Let's randomize why not...
    random.shuffle(feed.entries)
    for article in feed.entries:
	#This can take all night if it has to, we don't want to hammer the server into oblivios
	sleep(1)
        kw = fetch_article(article,titlefield=titlefield,linkfield=linkfield,niceify=niceify)
        if kw is None:
	    continue
	l = Link._submit(kw['title'],kw['link'],ac,sr,ip,spam=False)
	l._commit()
	l.set_url_cache()
	#We don't really need auto-submitted links to be vote on...
	queries.queue_vote(ac,l,True,ip,cheater=False)
	queries.new_link(l)
	changed(l)
	print "Submitted %s" % article[titlefield]
	sleep(.1)
    return
