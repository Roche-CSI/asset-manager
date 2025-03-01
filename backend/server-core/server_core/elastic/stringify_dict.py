import json
from typing import Any, Dict, Union, List, Tuple


class StringifyDict(dict):
    """
    A specialized dictionary class for preparing data for indexing.
    Handles type conversion, null value cleaning, and ensures proper JSON serialization.
    """

    @staticmethod
    def _prepare_value(value: Any) -> Union[str, List, Dict, None]:
        """
        Prepare a single value for indexing by converting to appropriate types.

        Args:
            value: Any value to be prepared

        Returns:
            Prepared value suitable for indexing
        """
        if value is None:
            return ""
        elif isinstance(value, (bool, int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            return [StringifyDict._prepare_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: StringifyDict._prepare_value(v) for k, v in value.items()}
        else:
            return str(value)

    @staticmethod
    def _remove_null(data: Union[Dict, List]) -> Union[Dict, List]:
        """
        Remove null values from data structure and clean nested structures.
        Handles both dictionaries and lists.

        Args:
            data: Dictionary or list to clean

        Returns:
            Union[Dict, List]: Cleaned data structure with null values removed
        """
        if isinstance(data, dict):
            if not data:
                return {}

            cleaned = {}
            for key, value in data.items():
                if value is None:
                    continue  # Skip null values
                elif isinstance(value, (dict, list)):
                    cleaned_value = StringifyDict._remove_null(value)
                    if cleaned_value or cleaned_value == []:  # Keep empty lists, skip empty dicts
                        cleaned[key] = cleaned_value
                else:
                    cleaned[key] = value
            return cleaned

        elif isinstance(data, list):
            cleaned = []
            for item in data:
                if item is None:
                    continue  # Skip null values
                elif isinstance(item, (dict, list)):
                    cleaned_item = StringifyDict._remove_null(item)
                    if cleaned_item or cleaned_item == []:  # Keep empty lists
                        cleaned.append(cleaned_item)
                else:
                    cleaned.append(item)
            return cleaned

        return data  # Return as is for other types

    def prepare(self):
        # make a copy of the current dictionary
        clone = json.loads(json.dumps(self))
        return self._prepare_value(self._remove_null(clone))