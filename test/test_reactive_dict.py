from unittest import TestCase
from unittest.mock import Mock
from becs.reactive_dict import EVT_ITEM_ADDED, EVT_ITEM_CHANGED, EVT_ITEM_REMOVED, ReactiveDict

class ReactiveDictTests(TestCase):

    def test_adding_items(self):
        rd = ReactiveDict()

        rd["item1"] = "item1 value"

        self.assertTrue(rd.get("item1") == "item1 value", "Could not check value")

    def test_item_added_event(self):
        rd = ReactiveDict()

        mock_added = Mock()
        mock_removed = Mock()
        mock_modified = Mock()

        rd.on(EVT_ITEM_ADDED, mock_added)
        rd.on(EVT_ITEM_REMOVED, mock_removed)
        rd.on(EVT_ITEM_REMOVED, mock_modified)

        rd["new_item"] = 1

        mock_added.assert_called_once_with(rd, "new_item", 1, None)
        mock_removed.assert_not_called()
        mock_modified.assert_not_called()

    def test_item_removed_event(self):
        rd = ReactiveDict()
        
        mock_added = Mock()
        mock_removed = Mock()
        mock_modified = Mock()

        rd.on(EVT_ITEM_ADDED, mock_added)
        rd.on(EVT_ITEM_REMOVED, mock_removed)
        rd.on(EVT_ITEM_CHANGED, mock_modified)

        rd["to_remove"] = 1
        del rd["to_remove"]

        mock_added.assert_called_once_with(rd, "to_remove", 1, None)
        mock_removed.assert_called_once_with(rd, "to_remove")
        mock_modified.assert_not_called()

    def test_item_modified_event(self):
        rd = ReactiveDict()
        
        mock_added = Mock()
        mock_removed = Mock()
        mock_modified = Mock()

        rd.on(EVT_ITEM_ADDED, mock_added)
        rd.on(EVT_ITEM_REMOVED, mock_removed)
        rd.on(EVT_ITEM_CHANGED, mock_modified)

        rd["to_modify"] = 1
        rd["to_modify"] = 2

        mock_added.assert_called_once_with(rd, "to_modify", 1, None)
        mock_removed.assert_not_called()
        mock_modified.assert_called_once_with(rd, "to_modify", 2, 1)

        # reading key resets its "changed" flag
        self.assertListEqual(rd.keys_changed(), ["to_modify"])
        no_op = rd.get("to_modify")
        self.assertListEqual(rd.keys_changed(), [])

        # reading key resets its "changed" flag
        rd["to_modify"] = 3
        self.assertListEqual(rd.keys_changed(), ["to_modify"])
        no_op = rd["to_modify"]
        self.assertListEqual(rd.keys_changed(), [])

        # looping over keys resets "changed" flag
        rd["to_modify1"] = 1
        rd["to_modify2"] = 2
        rd["to_modify3"] = 3
        rd["to_modify4"] = 4
        ## modify
        rd["to_modify1"] = 2
        rd["to_modify2"] = 3
        rd["to_modify3"] = 4
        rd["to_modify4"] = 5

        self.assertListEqual(rd.keys_changed(), ["to_modify1", "to_modify2", "to_modify3", "to_modify4"])
        rd.items()
        self.assertListEqual(rd.keys_changed(), [])
