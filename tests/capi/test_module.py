import unittest

class CAPIModuleTest(unittest.TestCase):
    def test_can_import_capi_module(self):
        try:
            import spotify.capi
        except ImportError:
            self.fail('Could not import spotify.capi module')
