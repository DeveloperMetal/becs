from time import time
from unittest import TestCase
from unittest.mock import Mock, call
from becs.atomic import MAX_SEQUENCE, AtomicID
from becs.exceptions import InvalidSystemClock


class TestAtomicIds(TestCase):
    def test_sequential(self):
        atid = AtomicID(0)

        ids = []
        for i in range(0, 100):
            ids.append(atid.next())

        last = -1
        for id in ids:
            self.assertTrue(id > last, "Sequence broken")
            last = id

    def test_sequential_multi_nodes(self):
        node1 = AtomicID(1)
        node2 = AtomicID(2)

        n1id1 = node1.next()
        n2id1 = node2.next()
        n1id2 = node1.next()
        n2id2 = node2.next()

        self.assertTrue(
            n1id1 < n1id2 and n1id1 < n2id1 and n1id2 < n2id1 and n2id1 < n2id2,
            "Node sequence broken",
        )

    def test_stall_for_new_sequence(self):
        node = AtomicID(1)

        timestamp = 123
        def mock_timestamp():
            nonlocal timestamp
            ret = timestamp
            timestamp += 1
            return ret

        # force end of sequence within a millisecond
        node._sequence = MAX_SEQUENCE
        node._last_timestamp = timestamp
        node._timestamp = Mock(side_effect=mock_timestamp)

        # stall for a new timestamp(1 millisecond)
        node.next()

        node._timestamp.assert_has_calls([call(), call()])
        self.assertEqual(node._sequence, 0)
        self.assertEqual(node._last_timestamp, 124)

    def test_custom_epoch_set(self):
        node = AtomicID(1, 100)
        
        self.assertEqual(node._epoch, 100)

    def test_invalid_system_click_exception(self):
        node = AtomicID(1, 100)

        node._last_timestamp = (int(time() * 1000) - node._epoch) + 10000
        with self.assertRaises(InvalidSystemClock):
            node.next()
