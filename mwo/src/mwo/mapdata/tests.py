from __future__ import absolute_import

import unittest
import logging

class TestTasks(unittest.TestCase):
    def test_call(self):
        from mwo.mapdata.celerytasks import beat_init_handler
#         from mwo.mapdata.views import StatusUpdateView
#         from .tasks import call
        
#         call(StatusUpdateView, 'onMapUpdated', StatusUpdateView())
        logging.basicConfig(level=logging.DEBUG)
        beat_init_handler()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
