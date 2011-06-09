try: # 2.7
    # pylint: disable = E0611,F0401
    from unittest.case import SkipTest
    # pylint: enable = E0611,F0401
except ImportError:
    try: # Nose
        from nose.plugins.skip import SkipTest
    except ImportError: # Failsafe
        class SkipTest(Exception):
            pass
