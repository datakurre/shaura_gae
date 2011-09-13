# -*- coding: utf-8 -*-
"""zope.testrunner layers"""

from pyramid import testing


class PyramidLayer(object):

    @classmethod
    def setUp(cls):
        cls.config = testing.setUp()

        import pyramid_zcml
        cls.config.include(pyramid_zcml)
        cls.config.load_zcml("shaura_gae:configure.zcml")

    @classmethod
    def tearDown(cls):
        testing.tearDown()

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class AppEngineLayer(PyramidLayer):

    @classmethod
    def setUp(cls):
        from google.appengine.ext import testbed

        # First, create an instance of the Testbed class.
        cls.testbed = testbed.Testbed()

    @classmethod
    def tearDown(cls):
        testing.tearDown()

    @classmethod
    def testSetUp(cls):
        # Then activate the testbed, which prepares the service stubs for use.
        cls.testbed.activate()

        # Next, declare which service stubs you want to use.
        cls.testbed.init_datastore_v3_stub()
        cls.testbed.init_memcache_stub()

    @classmethod
    def testTearDown(cls):
        cls.testbed.deactivate()
