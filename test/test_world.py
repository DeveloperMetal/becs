from unittest import TestCase
from unittest.mock import MagicMock, Mock, call
from becs import EVT_COMPONENT_DEFINED, EVT_COMPONENT_REMOVED, EVT_ENTITY_ADDED, EVT_ENTITY_REMOVED, World
from becs.exceptions import ComponentInstanceNotFound, ComponentNotFound, EntityNotFound
from becs.meta import ComponentMeta, FieldMeta


class WorldTests(TestCase):
    def test_add_entity(self):
        w = World()

        # mock internal api calls
        w._eid.next = Mock(return_value="123")
        w._cid.next = Mock(return_value="abc")
        w.fire = Mock()
        w.add_component = Mock()

        entity_id = w.add_entity("test")

        self.assertTrue(entity_id == "123")
        w.add_component.assert_called_once_with("123", "test")
        w.fire.assert_called_once_with(EVT_ENTITY_ADDED, "123", ("test",))

    def test_remove_entity(self):

        w = World()

        # Inject entity and component data to test remove only
        # This is the expected data structure to exist
        w._entities["123"] = {"test": "abc"}
        w._components["abc"] = {"field1": None}

        # mock expected internal api calls
        w.fire = Mock()
        w.remove_component = Mock()

        w.remove_entity("123")

        w.remove_component.assert_called_with("123", "test")
        w.fire.assert_called_with(EVT_ENTITY_REMOVED, "123")

    def test_define_component(self):
        w = World()

        # mock internal apis
        w._cid.next = Mock(return_value="abc")
        w.fire = Mock()
        comp_meta = ComponentMeta(
            "Test",
            "test",
            [
                FieldMeta("Field 1", "field1", str)
            ]
        )

        w.define_component(comp_meta)

        self.assertTrue(w._componentMeta["test"] == comp_meta)
        w.fire.assert_called_with(EVT_COMPONENT_DEFINED, comp_meta)

    def test_add_component(self):
        w = World()

        # mock internal apis
        w.fire = Mock()
        w._cid.next = Mock(return_value="abc")

        # mock internal data structure
        w._entities["123"] = {}
        w._componentMeta["test"] = MagicMock()
        w._componentMeta["test"].instantiate = Mock()

        cid = w.add_component("123", "test")

        w._cid.next.assert_called()
        w._componentMeta["test"].instantiate.assert_called()
        self.assertTrue(w._entities["123"]["test"] == "abc")
        self.assertTrue(cid == "abc")
        self.assertDictEqual(w._components[cid].tag, {
            "id": cid,
            "entity_id": "123",
            "component": "test"
        })

    def test_remove_component(self):
        w = World()

        # Mock internal apis
        w.fire = Mock()

        # Mock internal structure
        w._entities["123"] = {"test": "abc"}
        w._componentMeta["test"] = {}
        w._components["abc"] = {}

        self.assertTrue("abc" in w._components)
        self.assertTrue("test" in w._entities["123"])

        w.remove_component("123", "test")

        w.fire.assert_called_with(EVT_COMPONENT_REMOVED, "123", "abc", "test")
        self.assertTrue("abc" not in w._components)
        self.assertTrue("test" not in w._entities["123"])

    def test_get_component_meta(self):
        w = World()

        w._componentMeta["test"] = "test"

        self.assertEqual(w.get_component_meta("test"), "test")

    def test_get_component(self):
        w = World()

        w._entities["123"] = { "test": "abc" }
        w._components["abc"] = "some component"

        comp = w.get_component("123", "test")

        self.assertEqual(comp, "some component")

    def test_list_entity_components(self):
        w = World()

        w._entities["123"] = {"test": "abc", "test2": "def"}

        self.assertListEqual(list(w.list_entity_components("123")), ["test", "test2"])

    def test_entity_has_component(self):
        w = World()

        w._entities["123"] = {"test": "abc"}

        self.assertTrue(w.entity_has_component("123", "test"))
        self.assertFalse(w.entity_has_component("123", "missing"))

    def test_remove_entity_exception(self):
        w = World()

        with self.assertRaises(Exception):
            w.remove_entity("123")

    def test_remove_component_exceptions(self):
        w = World()

        with self.assertRaises(EntityNotFound):
            w.remove_component("123", "test")

        w._entities["123"] = {}

        with self.assertRaises(ComponentNotFound):
            w.remove_component("123", "test")

        w._entities["123"]["test"] = "abc"

        with self.assertRaises(ComponentInstanceNotFound):
            w.remove_component("123", "test")

    def test_add_component_exceptions(self):
        w = World()

        with self.assertRaises(EntityNotFound):
            w.add_component("123", "test")

        w._entities["123"] = {}

        with self.assertRaises(ComponentNotFound):
            w.add_component("123", "test")

    def test_get_component_meta_exceptions(self):
        w = World()

        with self.assertRaises(ComponentNotFound):
            w.get_component_meta("test")

    def test_list_entities_exceptions(self):
        w = World()

        with self.assertRaises(EntityNotFound):
            w.list_entity_components("123")

    def test_entity_has_component_exceptions(self):
        w = World()

        with self.assertRaises(EntityNotFound):
            w.entity_has_component("123", "test")

    def test_get_component_exceptions(self):
        w = World()

        with self.assertRaises(EntityNotFound):
            w.get_component("123", "test")

        w._entities["123"] = {}

        with self.assertRaises(ComponentNotFound):
            w.get_component("123", "test")

        w._entities["123"]["test"] = "abc"

        with self.assertRaises(ComponentInstanceNotFound):
            w.get_component("123", "test")
