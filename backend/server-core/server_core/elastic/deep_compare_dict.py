import json
from typing import Any, Dict


class DeepCompareDict(dict):
    """
    A special dictionary class that provides advanced comparison capabilities,
    particularly useful for handling nested structures, lists, and document comparisons.
    """

    @staticmethod
    def _is_equal(val1: Any, val2: Any) -> bool:
        """
        Compare two values with special handling for lists and dicts.
        Lists are sorted if possible, and dicts are compared after converting to sorted JSON.

        Args:
            val1: First value to compare
            val2: Second value to compare

        Returns:
            bool: True if values are considered equal, False otherwise
        """
        if val1 is None and val2 is None:
            return True

        if val1 is None or val2 is None:
            return False

        # Handle lists
        if isinstance(val1, list) and isinstance(val2, list):
            try:
                # Try sorting if elements are comparable
                val1_sorted = sorted(val1)
                val2_sorted = sorted(val2)
                return json.dumps(val1_sorted, sort_keys=True) == json.dumps(val2_sorted, sort_keys=True)
            except TypeError:
                # If elements aren't sortable (e.g., dicts in list), compare JSON strings
                return json.dumps(val1, sort_keys=True) == json.dumps(val2, sort_keys=True)

        # Handle dictionaries
        if isinstance(val1, dict) and isinstance(val2, dict):
            return json.dumps(val1, sort_keys=True) == json.dumps(val2, sort_keys=True)

        # Handle basic types
        return val1 == val2

    def get_updates(self, other: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare this dictionary with another and return a dict of changed fields.
        Handles nested structures and lists with proper comparison.

        Args:
            other: Dictionary to compare against

        Returns:
            Dict containing only the fields that have changed
        """
        updates = {}

        for key, new_value in other.items():
            old_value = self.get(key)

            if not self._is_equal(old_value, new_value):
                updates[key] = new_value

        return updates

    def __eq__(self, other: Any) -> bool:
        """
        Override equality comparison to use our special comparison logic.

        Args:
            other: Object to compare with

        Returns:
            bool: True if objects are considered equal, False otherwise
        """
        if not isinstance(other, (dict, DeepCompareDict)):
            return False

        if len(self) != len(other):
            return False

        return all(self._is_equal(self.get(key), other.get(key)) for key in self)

    def update_if_changed(self, other: Dict[str, Any]) -> bool:
        """
        Update this dictionary with values from another dict, but only if they're different.

        Args:
            other: Dictionary containing new values

        Returns:
            bool: True if any updates were made, False otherwise
        """
        updates = self.get_updates(other)
        if updates:
            self.update(updates)
            return True

        return False

