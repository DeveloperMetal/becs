from dataclasses import dataclass
from typing import Any, Dict, List, Type

from becs.reactive_dict import ReactiveDict

@dataclass
class FieldMeta:
    label: str
    field_name: str
    field_type: Type
    default_value: Any = None

@dataclass
class ComponentMeta:
    label: str
    component_name: str
    fields: List[FieldMeta]

    def __post_init__(self):
        assert(isinstance(self.fields, list))
        assert(isinstance(self.component_name, str))
        assert(isinstance(self.label, str))

    def instantiate(self):
        return ReactiveDict({ field.field_name: field.default_value for field in self.fields })