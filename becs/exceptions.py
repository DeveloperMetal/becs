class EntityNotFound(Exception):
    def __init__(self, entity_id: str):
        super().__init__("Entity not found: {}".format(entity_id))
        self.entity_id = entity_id


class ComponentNotFound(Exception):
    def __init__(self, component):
        super().__init__("Component not found: {}".format(component))
        self.component = component

class ComponentInstanceNotFound(Exception):
    def __init__(self, component_id):
        super().__init__("Component instance not found: {}".format(component_id))
        self.component_id = component_id

class InvalidSystemClock(Exception):
    pass