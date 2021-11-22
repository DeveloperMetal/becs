from unittest import TestCase
from unittest.mock import Mock
from becs.events import EventDispatcherMixin

class TestEvents(TestCase):

    def test_on(self):
        ev = EventDispatcherMixin()
        
        self.assertIsNone(getattr(ev, "_EventDispatcherMixin__events", None))

        cb = Mock()
        ev.on("test", cb)

        self.assertIsNotNone(getattr(ev, "_EventDispatcherMixin__events", None))
        self.assertDictEqual(getattr(ev, "_EventDispatcherMixin__events", None), { "test": [cb] })

    def test_off(self):
        ev = EventDispatcherMixin()
        
        self.assertIsNone(getattr(ev, "_EventDispatcherMixin__events", None))

        cb = Mock()
        ev.off("test", cb)

        self.assertIsNotNone(getattr(ev, "_EventDispatcherMixin__events", None))

        getattr(ev, "_EventDispatcherMixin__events")["test"] = [cb]

        ev.off("test", cb)

        self.assertDictEqual(getattr(ev, "_EventDispatcherMixin__events", None), { "test": [] })

    def test_fire(self):

        ev = EventDispatcherMixin()
        cb = Mock()

        setattr(ev, "_EventDispatcherMixin__events", {"test": [cb]})

        ev.fire("test", 1, 2, 3)

        cb.assert_called_once_with(1, 2, 3)