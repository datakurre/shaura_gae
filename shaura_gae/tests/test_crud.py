# -*- coding: utf-8 -*-
"""Integration tests"""

import unittest2 as unittest
from corejet.core import Scenario, story, scenario, given, when, then

from shaura_gae import testing


@story(id="17916955", title=(u"As developer I want to store "
                             u"'zope.schema'-modeled data on AppEngine"))
class I_want_to_store_zopeschemamodeled_data_on_AppEngine(unittest.TestCase):

    layer = testing.AppEngineLayer

    def redo(self, name):
        index = [s.name for s in self.scenarios].index(name)
        scenario = self.scenarios[index]
        for clause in scenario.givens + scenario.whens + scenario.thens:
            clause(self)

    @scenario("Save a new object into AppEngine datastore")
    class Save_a_new_object_into_AppEngine_datastore(Scenario):

        @given("I've got a new 'zope.schema'-modeled object")
        def Ive_got_a_new_zopeschemamodeled_object(self):
            import zope.interface
            import zope.schema

            class ITask(zope.interface.Interface):
                title = zope.schema.TextLine()

            import shaura_gae.db

            class Task(shaura_gae.db.Model):
                zope.interface.implements(ITask)

            self.task = Task(title=u"Custom title")

        @when("I save it")
        def I_save_it(self):
            from shaura_core.interfaces import IObjectManager
            manager = self.layer.config.registry.getUtility(IObjectManager)
            manager.add(self.task)

        @then("I can retrieve it from AppEngine datastore")
        def I_can_retrieve_it_from_AppEngine_datastore(self):
            from shaura_core.interfaces import IObjectManager

            manager = self.layer.config.registry.getUtility(IObjectManager)

            query = {
                "object_type": self.task.__class__.__name__,
                "__key__": self.task.key()  # GAE internal datastore key
            }
            self.results = tuple(manager(**query))
            self.assertEquals(len(self.results), 1)
            self.assertEquals(self.task.key(), self.results[0].key())
            self.assertEquals(self.task.title, self.results[0].title)

    @scenario("Modify a saved object in AppEngine datastore")
    class Modify_a_saved_object_in_AppEngine_datastore(Scenario):

        @given("I've retrieved a 'zope.schema'-modeled object from datastore")
        def Ive_retrieved_a_zopeschemamodeled_object_from_datastore(self):
            self.redo("Save a new object into AppEngine datastore")
            self.task = self.results[0]

        @when("I modify it")
        def I_modify_it(self):
            self.task.title = u"Modified title"

        @when("I save it")
        def I_save_it(self):
            from shaura_core.interfaces import IObjectManager
            manager = self.layer.config.registry.getUtility(IObjectManager)
            manager.update(self.task)

        @then("I can retrieve it from AppEngine datastore again")
        def I_can_retrieve_it_from_AppEngine_datastore_again(self):
            from shaura_core.interfaces import IObjectManager

            manager = self.layer.config.registry.getUtility(IObjectManager)

            query = {
                "object_type": self.task.__class__.__name__,
                "__key__": self.task.key()  # GAE internal datastore key
            }
            self.results = tuple(manager(**query))

        @then("It has the changes I've made")
        def It_has_the_changes_Ive_made(self):
            self.assertEquals(len(self.results), 1)
            self.assertEquals(self.task.key(), self.results[0].key())
            self.assertEquals(self.task.title, self.results[0].title)

    @scenario("Delete a saved object from AppEngine datastore")
    class Delete_a_saved_object_from_AppEngine_datastore(Scenario):

        @given("I've retrieved a 'zope.schema'-modeled object from datastore")
        def Ive_retrieved_a_zopeschemamodeled_object_from_datastore(self):
            self.redo("Save a new object into AppEngine datastore")
            self.task = self.results[0]

        @when("I delete it")
        def I_delete_it(self):
            from shaura_core.interfaces import IObjectManager
            manager = self.layer.config.registry.getUtility(IObjectManager)
            manager.delete(self.task)

        @then("I cannot retrieve it from AppEngine datastore anymore")
        def I_cannot_retrieve_it_from_AppEngine_datastore_anymore(self):
            from shaura_core.interfaces import IObjectManager

            manager = self.layer.config.registry.getUtility(IObjectManager)

            query = {
                "object_type": self.task.__class__.__name__,
            }
            self.results = tuple(manager(**query))

            self.assertEquals(len(self.results), 0)
