from typing import Any, Callable, Dict, List, Optional, Type
from becs.atomic import AtomicID
from becs.exceptions import ComponentInstanceNotFound, ComponentNotFound, EntityNotFound
from becs.meta import ComponentMeta, FieldMeta
from becs.reactive_dict import (
    EVT_ITEM_ADDED,
    EVT_ITEM_CHANGED,
    EVT_ITEM_REMOVED,
    ReactiveDict,
)
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
    _componentQueues: Dict[str, List[ReactiveDict]]
    _systems: Dict[str, List[Callable]]
    _eid: AtomicID
    _cid: AtomicID
    _node_id: int = 1
    _executing: Dict[str, bool] = {}
    _execute_next: List[str] = []

    def __init__(self, node_id: Optional[int] = None):
        self._entities = dict()
        self._components = dict()
        self._componentMeta = dict()
        self._systems = dict()
        self._executing = dict()
        self._execute_next = []

        if node_id:
            self._node_id = node_id

        self._eid = AtomicID(node_id=self._node_id)
        self._cid = AtomicID(node_id=self._node_id)

    async def run(self):

        while len(self._execute_next) > 0:
            next = self._execute_next.copy()
            self._execute_next.clear()

            for component in next:
                self.execute_queue(component)

    def define_component(self, meta: ComponentMeta):
        self._componentMeta[meta.component_name] = meta
        self._componentQueues[meta.component_name] = []
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
        comp_instance.tag = {"id": id, "entity_id": entity_id, "component": component}
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

    def _on_component_modified(self, component: ReactiveDict, key, value):
        comp_name = component.tag.get("component")
        if component not in self._componentQueues[comp_name]:
            self._componentQueues[comp_name].append(component)

        if comp_name not in self._execute_next:
            self._execute_next.append(comp_name)

        self.execute_queue(comp_name)

    def execute_queue(self, component):
        if (
            len(self._componentQueues[component]) > 0
            and component in self._systems
            and self._executing.get(component, False)
        ):

            self._executing[component] = True

            try:
                # copy systems list to avoid issues with dynamic systems being added
                # by other systems
                systems = self._systems[component].copy()
                for system in systems:
                    try:
                        system(self._componentQueues[component])
                    except Exception as ex:
                        print(ex)

            finally:
                self._componentQueues[component].clear()
                self._executing[component] = False
