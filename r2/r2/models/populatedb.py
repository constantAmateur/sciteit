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
from r2.models import *
from r2.lib.utils import fetch_things2
from pylons import g
from r2.lib.db import queries
from copy import copy


import string
import random

def random_word(min, max):
    return ''.join([ random.choice(string.letters)
                         for x
                         in range(random.randint(min, max)) ])


def scour_sciteits(minid=0,maxid=10000):
    #Do the root ID
    root = Subsciteit._by_name(g.default_sr)
    root.children=[]
    root.parent=None
    root._commit()
    #Set everything else to a root category
    tmp = range(minid,maxid)
    tmp.remove(root._id)
    #Get the bad indexes and remove them...
    try:
        allcats = Subsciteit._byID(tmp)
    except NotFound, e:
        bad = [int(a) for a in e.message[12:-1].split(',')]
        tmp = [a for a in tmp if not a in bad]
        allcats = Subsciteit._byID(tmp)
    
    tmp=[]
    for cat in allcats.values():
        cat.children=[]
        cat.parent=root._id
        tmp.append(cat._id)
        cat._commit()
    
    root = Subsciteit._by_name(g.default_sr)
    root.children=tmp
    root._commit()
    print "Scoured %s sciteits!" % len(allcats)
    return


def initialize():
    try:
        a = Account._by_name(g.system_user)
    except NotFound:
        a = register(g.system_user, "password")

    #Must have the root category, so make it first...
    try:
        root = Subsciteit._new(name = g.default_sr, 
                               title = g.default_sr,
                               ip = '0.0.0.0',
                               author_id = a._id,
                               type = 'restricted',
                               lang = g.lang)
        root._commit()
    except SubsciteitExists:
        root = Subsciteit._by_name(g.default_sr)

    made = []
    root_cats=[]
    root_defaults = dict(title = '',
                     author_id = a._id, 
                     ip = '0.0.0.0', 
                     type = 'public',
                     link_type = 'any',
                     parent = root._id,
                     children = [],
                     lang = g.lang)
    
    root_cats.append(dict(root_defaults.items()+dict(name="scitedev",
                                                title="Help develop sciteit?",
                                                description="""Most of the development of sciteit requires knowledge of the sciteit code, which is not something most people have. However, there are some things that can be done without any knowledge of the nitty gritty details of how sciteit works. They will be posted here. If you'd like to help out, we'd love your help.
    If you have a feature request, please post it in ideasfortheadmins.
    If you have a bug report, please post it in bugs.""",
                                                link_type='self').items()))
    
    root_cats.append(dict(root_defaults.items()+dict(name="bugs",
                                                title="Did something break?",
                                                description="""This is the place to post bug reports. As sciteit is still in beta, there will probably be quite a few of these. We very much appreciate you taking the time to let us know when things go wrong. If you have a feature request, please post it in ideasfortheadmins.
    ou would like to help out with the development of the site, post a message to scitedev.""",
                                                link_type='self').items()))
    
    root_cats.append(dict(root_defaults.items()+dict(name="ideasfortheadmins",
                                                title="Feature requests",
                                                description="""This is the place to post feature requests. If you have an idea that you think would improve the site, please post it here.
    ou have a bug report, please post it in bugs.
    ou would like to help out with the development of the site, post a message to scitedev.""",
                                                link_type='self').items()))
    
    root_cats.append(dict(root_defaults.items()+dict(name="howdoi",
                                                title="Help using sciteit",
                                                description="""If you have a question that is not answered in the help, post a question about it here.""",
                                                link_type='self').items()))
    
    root_cats.append(dict(root_defaults.items()+dict(name="physics",title='physics').items()))
    root_cats.append(dict(root_defaults.items()+dict(name="chemistry",title="chemistry").items()))
    root_cats.append(dict(root_defaults.items()+dict(name="mathematics",title="mathematics").items()))
    root_cats.append(dict(root_defaults.items()+dict(name="biology",title="biology").items()))
    root_cats.append(dict(root_defaults.items()+dict(name="history",title="history").items()))
    #root_cats.append(dict(root_defaults.items()+dict(name="anthropology",title="anthropology").items()))
    
    #Finally make them all
    for cat in root_cats:
        try:
            sr = Subsciteit._new(**cat)
            sr._commit()
            made.append(sr)
        except SubsciteitExists:
            print "%s already exists!" % cat['name']
    	sr = Subsciteit._by_name(cat['name'])
        root=Subsciteit._by_name(g.default_sr)
        tmp=copy(root.children)
        if not sr._id in tmp:
            tmp.append(sr._id)
    	root.children=tmp
    	root._commit()
    
    return len(made) 




def populate(num_srs = 10, num_users = 1000, num_links = 100, num_comments = 20, num_votes = 50):
    try:
        a = Account._by_name(g.system_user)
    except NotFound:
        a = register(g.system_user, "password")

    srs = []
    for i in range(num_srs):
        name = "sciteit_test%d" % i
        try:
            sr = Subsciteit._new(name = name, title = "everything about #%d"%i,
                                ip = '0.0.0.0', author_id = a._id)
            sr._downs = 10
            sr.lang = "en"
            sr._commit()
        except SubsciteitExists:
            sr = Subsciteit._by_name(name)
        srs.append(sr)

    accounts = []
    for i in range(num_users):
        name_ext = ''.join([ random.choice(string.letters)
                             for x
                             in range(int(random.uniform(1, 10))) ])
        name = 'test_' + name_ext
        try:
            a = register(name, name)
        except AccountExists:
            a = Account._by_name(name)
        accounts.append(a)

    for i in range(num_links):
        id = random.uniform(1,100)
        title = url = 'http://google.com/?q=' + str(id)
        user = random.choice(accounts)
        sr = random.choice(srs)
        l = Link._submit(title, url, user, sr, '127.0.0.1')
        queries.new_link(l)

        comments = [ None ]
        for i in range(int(random.betavariate(2, 8) * 5 * num_comments)):
            user = random.choice(accounts)
            body = ' '.join([ random_word(1, 10)
                              for x
                              in range(int(200 * random.betavariate(2, 6))) ])
            parent = random.choice(comments)
            (c, inbox_rel) = Comment._new(user, l, parent, body, '127.0.0.1')
            queries.new_comment(c, inbox_rel)
            comments.append(c)
            for i in range(int(random.betavariate(2, 8) * 10)):
                another_user = random.choice(accounts)
                v = Vote.vote(another_user, c, True, '127.0.0.1')
                queries.new_vote(v)

        like = random.randint(50,100)
        for i in range(int(random.betavariate(2, 8) * 5 * num_votes)):
           user = random.choice(accounts)
           v = Vote.vote(user, l, random.randint(0, 100) <= like, '127.0.0.1')
           queries.new_vote(v)

    queries.worker.join()


def by_url_cache():
    q = Link._query(Link.c._spam == (True,False),
                    data = True,
                    sort = desc('_date'))
    for i, link in enumerate(fetch_things2(q)):
        if i % 100 == 0:
            print "%s..." % i
        link.set_url_cache()
