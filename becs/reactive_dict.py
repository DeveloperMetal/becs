from typing import Any, Dict, List, Optional
from becs.events import EventDispatcherMixin

EVT_ITEM_ADDED = "item-added"
EVT_ITEM_REMOVED = "item-removed"
EVT_ITEM_CHANGED = "item-changed"


class ReactiveDict(Dict[str, Any], EventDispatcherMixin):
    def __init__(self, *kargs, **kwargs):
        self.__keys_changed: List = []
        super().__init__(*kargs, **kwargs)

    def __setitem__(self, __k, v) -> None:
        evt = None
        old_val = self.get(__k, None)
        if not old_val:
            evt = EVT_ITEM_ADDED
        elif old_val != v:
            evt = EVT_ITEM_CHANGED
            self.__keys_changed.append(__k)

        result = super().__setitem__(__k, v)

        self.fire(evt, self,  __k, v, old_val)
        return result

    def __delitem__(self, __v) -> None:
        super().__delitem__(__v)
        self.fire(EVT_ITEM_REMOVED, self, __v)

    def __getitem__(self, __k):
        if __k in self.__keys_changed:
            self.__keys_changed.remove(__k)
        return super().__getitem__(__k)

    def items(self):
        self.__keys_changed.clear()
        return super().items()

    def keys_changed(self) -> List[str]:
        return self.__keys_changed

    def get(self, key:str, default: Optional[Any] = None) -> Any:
        if key in self.__keys_changed:
            self.__keys_changed.remove(key)
        return super().get(key, default)