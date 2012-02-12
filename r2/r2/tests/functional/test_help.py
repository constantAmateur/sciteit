from r2.tests import *

class TestHelpController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='help'))
        # Test response...
