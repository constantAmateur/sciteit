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
from sciteit_base import SciteitController, MinimalController, make_key
from r2.lib.pages import Button, ButtonNoBody, ButtonEmbed, ButtonLite, \
    ButtonDemoPanel, WidgetDemoPanel, Bookmarklets, BoringPage, UpgradeButtons
from r2.lib.pages.things import wrap_links
from r2.models import *
from r2.lib.utils import tup, query_string
from pylons import c, request
from validator import *
from pylons.i18n import _
from r2.lib.filters import spaceCompress
from r2.controllers.listingcontroller import ListingController

class ButtonjsController(MinimalController):
    def pre(self):
        MinimalController.pre(self)
        # override user loggedin behavior to ensure this page always
        # uses the page cache
        (user, maybe_admin) = \
            valid_cookie(c.cookies[g.login_cookie].value
                         if g.login_cookie in c.cookies
                         else '')
        if user:
            self.user_is_loggedin = True

    @validate(buttontype = VInt('t', 1, 5),
              url = VSanitizedUrl("url"),
              _height = VInt('height', 0, 300),
              _width = VInt('width', 0, 800),
              autohide = VBoolean("autohide"))
    def GET_button_embed(self, buttontype, _height, _width, url, autohide):
        # no buttons on domain listings
        if isinstance(c.site, DomainSR):
            return self.abort404()
        c.render_style = 'js'
        c.response_content_type = 'text/javascript; charset=UTF-8'
        if not c.user_is_loggedin and autohide:
            c.response.content = "void(0);"
            return c.response

        buttontype = buttontype or 1
        width, height = ((120, 22), (51, 69), (69, 52),
                         (51, 52), (600, 52))[min(buttontype - 1, 4)]
        if _width: width = _width
        if _height: height = _height

        bjs = ButtonEmbed(button=buttontype,
                          width=width,
                          height=height,
                          url = url,
                          referer = request.referer).render()
        return self.sendjs(bjs, callback='', escape=False)

    def request_key(self):
        return make_key('button_request_key',
                        c.lang,
                        c.content_langs,
                        request.host,
                        c.cname,
                        request.referer,
                        request.fullpath)

class ButtonsController(SciteitController):
    def buttontype(self):
        b = request.get.get('t') or 1
        try: 
            return int(b)
        except ValueError:
            return 1

    def get_wrapped_link(self, url, link = None, wrapper = None):
        try:
            links = []
            if link:
                links = [link]
            else:
                sr = None if isinstance(c.site, FakeSubsciteit) else c.site
                try:
                    links = tup(Link._by_url(url, sr))
                except NotFound:
                    pass

            if links:
                kw = {}
                if wrapper:
                    links = wrap_links(links, wrapper = wrapper)
                else:
                    links = wrap_links(links)
                links = list(links)
                links = max(links, key = lambda x: x._score) if links else None
            if not links and wrapper:
                return wrapper(None)
            return links
            # note: even if _by_url successed or a link was passed in,
            # it is possible link_listing.things is empty if the
            # link(s) is/are members of a private sciteit
            # return the link with the highest score (if more than 1)
        except:
            #we don't want to return 500s in other people's pages.
            import traceback
            g.log.debug("FULLPATH: get_link error in buttons code")
            g.log.debug(traceback.format_exc())
            if wrapper:
                return wrapper(None)


    def GET_button_content(self, *a, **kw):
        return """
        <html>
        <head>
        </head>
        <body style='border:1px solid #336699;text-align:center;margin:0px'>
           <a href='http://www.sciteit.com/upgradebuttons' target='_top' style='color:red'>upgrade</a>
        </body>
        </html>
        """

    @validate(buttontype = VInt('t', 1, 5),
              url = VSanitizedUrl("url"),
              _height = VInt('height', 0, 300),
              _width = VInt('width', 0, 800),
              autohide = VBoolean("autohide"))
    def GET_button_embed(self, buttontype, _height, _width, url, autohide):
        # no buttons on domain listings
        if isinstance(c.site, DomainSR):
            return self.abort404()
        c.render_style = 'js'
        c.response_content_type = 'text/javascript; charset=UTF-8'
        if not c.user_is_loggedin and autohide:
            c.response.content = "void(0);"
            return c.response

        buttontype = buttontype or 1
        width, height = ((120, 22), (51, 69), (69, 52),
                         (51, 52), (600, 52))[min(buttontype - 1, 4)]
        if _width: width = _width
        if _height: height = _height

        bjs = ButtonEmbed(button=buttontype,
                          width=width,
                          height=height,
                          url = url,
                          referer = request.referer).render()
        # we doing want the JS to be cached (it is referer dependent)
        c.used_cache = True
        return self.sendjs(bjs, callback='', escape=False)

    @validate(buttonimage = VInt('i', 0, 14),
              title = nop('title'),
              url = VSanitizedUrl('url'),
              newwindow = VBoolean('newwindow', default = False),
              styled = VBoolean('styled', default=True))
    def GET_button_lite(self, buttonimage, title, url, styled, newwindow):
        c.render_style = 'js'
        c.response_content_type = 'text/javascript; charset=UTF-8'

        if not url:
            url = request.referer
            # we don't want the JS to be cached if the referer was involved.
            c.used_cache = True

        def builder_wrapper(thing = None):
            kw = {}
            if not thing:
                kw['url'] = url
                kw['title'] = title
            return ButtonLite(thing,
                              image = 1 if buttonimage is None else buttonimage,
                              target = "_new" if newwindow else "_parent",
                              styled = styled, **kw)

        bjs = self.get_wrapped_link(url, wrapper = builder_wrapper)
        return self.sendjs(bjs.render(), callback='', escape=False)



    def GET_button_demo_page(self):
        # no buttons for domain listings -> redirect to top level
        if isinstance(c.site, DomainSR):
            return self.redirect('/buttons')
        return BoringPage(_("sciteit buttons"),
                          show_sidebar = False, 
                          content=ButtonDemoPanel()).render()

    def GET_upgrade_buttons(self):
        # no buttons for domain listings -> redirect to top level
        if isinstance(c.site, DomainSR):
            return self.redirect('/buttons')
        return BoringPage(_("sciteit buttons"),
                          show_sidebar = False, 
                          content=UpgradeButtons()).render()


    def GET_widget_demo_page(self):
        return BoringPage(_("sciteit widget"),
                          show_sidebar = False, 
                          content=WidgetDemoPanel()).render()

    def GET_bookmarklets(self):
        return BoringPage(_("bookmarklets"),
                          show_sidebar = False, 
                          content=Bookmarklets()).render()

    def GET_iphonebookmarklets(self):
        return BoringPage(_("submit"),
                          title = "submit to sciteit",
                          show_sidebar = False, 
                          content=Bookmarklets()).render()


