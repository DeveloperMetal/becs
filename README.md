# BECS

An [entity, component and systems library](https://en.wikipedia.org/wiki/Entity_component_system) with universal unique ids peppered for distributed use.

## Usage

Starts with a world:

```python
from bec import World
w = World()
```

Then define your components:

```python
from bec import World
from bec.meta import ComponentMeta, FieldMeta

w = World()

# define as many components as you want
w.define_component(ComponentMeta(
    "Test Component",
    "test_component",
    [
        FieldMeta("Field 1", "field1", str, "123")
    ]
))
```

Once you have defined a few components add them to your entities:

```python
entity_id = w.add_entity("component1", "component2")
```

Currently the library will return entity ids. Future versions will return a class instance for ease of use.

Check if an entity has a particular component:
```python
entity_id = w.add_entity("component1")
w.entity_has_component(entity_id, "component1") # True
w.entity_has_component(entity_id, "missing_component") # False
```

List components:
```python
entity_id = w.add_entity("component1", "component2")
w.list_entity_components(entity_id) # ["component1", "component2"]
```

Get an entity component's instance
```python
entity_id = w.add_entity("component1", "component2")
component = w.get_component(entity_id, "component1")
```

TODO: Add systems, systems tests and documentation
```