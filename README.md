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

```
TODO: Add systems, systems tests and documentation
```