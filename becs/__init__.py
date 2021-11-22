from typing import Any, Dict, List, Optional, Type
from becs.atomic import AtomicID
from becs.exceptions import ComponentInstanceNotFound, ComponentNotFound, EntityNotFound
from becs.meta import ComponentMeta, FieldMeta
from becs.reactive_dict import EVT_ITEM_ADDED, EVT_ITEM_CHANGED, EVT_ITEM_REMOVED, ReactiveDict
from becs.events import EventDispatcherMixin

EVT_ENTITY_ADDED = "entity-added"
EVT_ENTITY_REMOVED = "entity-removed"
EVT_COMPONENT_ADDED = "component-added"
EVT_COMPONENT_REMOVED = "component-removed"
EVT_COMPONENT_DEFINED = "component-defined"


class World(EventDispatcherMixin):
    _entities: Dict[str, Dict[str, str]]
    _components: Dict[str, ReactiveDict]
    _componentMeta: Dict[str, ComponentMeta]
    _eid: AtomicID
    _cid: AtomicID
    _node_id: int = 1

    def __init__(self, node_id: Optional[int] = None):
        self._entities = dict()
        self._components = dict()
        self._componentMeta = dict()

        if node_id:
            self._node_id = node_id

        self._eid = AtomicID(node_id=self._node_id)
        self._cid = AtomicID(node_id=self._node_id)

    def define_component(self, meta: ComponentMeta):
        self._componentMeta[meta.component_name] = meta
        self.fire(EVT_COMPONENT_DEFINED, meta)

    def add_entity(self, *components: List[str]):
        id = str(self._eid.next())
        if id not in self._entities:
            self._entities[id] = dict()

        for comp in components:
            self.add_component(id, comp)

        self.fire(EVT_ENTITY_ADDED, id, components)

        return id

    def remove_entity(self, entity_id: str):
        if entity_id not in self._entities:
            raise EntityNotFound(entity_id)

        components = set(self._entities[entity_id].keys())
        for comp_name in components:
            self.remove_component(entity_id, comp_name)

        del self._entities[entity_id]
        self.fire(EVT_ENTITY_REMOVED, entity_id)

    def add_component(self, entity_id: str, component: str):
        if entity_id not in self._entities:
            raise EntityNotFound(entity_id)

        if component not in self._componentMeta:
            raise ComponentNotFound(component)
        
        id = str(self._cid.next())

        meta = self._componentMeta[component]
        comp_instance = meta.instantiate()
        comp_instance.tag = {
            "id": id,
            "entity_id": entity_id,
            "component": component
        }
        comp_instance.on(EVT_ITEM_CHANGED, self._on_component_modified)

        self._components[id] = comp_instance
        self._entities[entity_id][component] = id

        self.fire(EVT_COMPONENT_ADDED, entity_id, id, component)

        return id

    def get_component_meta(self, component: str):
        if component not in self._componentMeta:
            raise ComponentNotFound(component)

        return self._componentMeta[component]

    def get_component(self, entity_id: str, component: str):
        if entity_id not in self._entities:
            raise EntityNotFound(entity_id)

        entity = self._entities[entity_id]

        if component not in entity:
            raise ComponentNotFound("component")

        cid = entity[component]

        if cid not in self._components:
            raise ComponentInstanceNotFound(cid)

        return self._components[cid]

    def list_entity_components(self, entity_id: str):
        if entity_id not in self._entities:
            raise EntityNotFound(entity_id)

        return self._entities[entity_id].keys()

    def entity_has_component(self, entity_id: str, component: str):
        if entity_id not in self._entities:
            raise EntityNotFound(entity_id)

        return component in self._entities[entity_id]

    def remove_component(self, entity_id: str, component: str):
        if entity_id not in self._entities:
            raise EntityNotFound(entity_id)

        if component not in self._entities[entity_id]:
            raise ComponentNotFound(component)

        cid = self._entities[entity_id][component]
        del self._entities[entity_id][component]

        if cid not in self._components:
            raise ComponentInstanceNotFound(cid)

        self._components[cid].off(EVT_ITEM_CHANGED, self._on_component_modified)

        del self._components[cid]

        self.fire(EVT_COMPONENT_REMOVED, entity_id, cid, component)

    def _on_component_modified(self, component, key, value):
        pass