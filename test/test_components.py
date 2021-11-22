from dataclasses import asdict
from unittest import TestCase
from becs import World
from becs.meta import ComponentMeta, FieldMeta

class ComponentTests(TestCase):
    def test_define_component(self):
        comp_def = ComponentMeta(
            "Test Component",
            "test_component",
            [
                FieldMeta("Field 1", "field1", str),
                FieldMeta("Field 2", "field2", str),
                FieldMeta("Field 3", "field3", str)
            ]
        )

        self.assertDictEqual(asdict(comp_def), {
            "label": "Test Component",
            "component_name": "test_component",
            "fields": [
                {
                    "label": "Field 1",
                    "field_name": "field1",
                    "field_type": str,
                    "default_value": None
                },
                {
                    "label": "Field 2",
                    "field_name": "field2",
                    "field_type": str,
                    "default_value": None
                },
                {
                    "label": "Field 3",
                    "field_name": "field3",
                    "field_type": str,
                    "default_value": None
                }
            ]
        })

        w = World(1)
        w.define_component(comp_def)

        self.assertTrue("test_component" in w._componentMeta)
        
    def test_instantiate_component(self):
        comp_def = ComponentMeta(
            "Test Component",
            "test_component",
            [
                FieldMeta("Field 1", "field1", str),
                FieldMeta("Field 2", "field2", str),
                FieldMeta("Field 3", "field3", str, "123")
            ]
        )

        instance = comp_def.instantiate()

        self.assertDictEqual(instance, {
            "field1": None,
            "field2": None,
            "field3": "123"
        })

