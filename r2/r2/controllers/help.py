import logging

from r2.lib.wrapped import Wrapped, Templated, CachedTemplate
from sciteit_base import SciteitController
from r2.lib.pages import HelpBlurb, BoringPage
from pylons import c,g, request

class HelpController(SciteitController):

    def GET_index(self,what='faq'):
    	""" I know this isn't in keeping with the rest of the code's ethos, but I didn't write that code, and I did write this so fuck it I say...."""
	#This will try and find a template of the format help_name...
	klass = type(str('help_'+what), (Templated,),{})
	try:
	    return BoringPage(what,content=klass()).render()
	except NotImplementedError:
	    self.abort404()
