from typing import Callable, Dict, List


class EventDispatcherMixin:
    def on(self, event: str, callback: Callable):
        if not getattr(self, "_EventDispatcherMixin__events", None):
            self.__events: Dict[str, List[Callable]] = dict()

        if event not in self.__events:
            self.__events[event] = []

        self.__events[event].append(callback)

    def fire(self, event, *kargs, **kwargs):
        if not getattr(self, "_EventDispatcherMixin__events", None):
            self.__events = dict()

        if event in self.__events:
            for callback in self.__events[event]:
                callback(*kargs, **kwargs)
