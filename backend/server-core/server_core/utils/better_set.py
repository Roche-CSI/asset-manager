from collections import OrderedDict
import copy


class BetterSet:
    """Custom Set for Objects"""

    def __init__(self, *args):
        self._dict = OrderedDict()
        for arg in args:
            self.add(arg)

    @property
    def items(self):
        """ Return a list containing all items in sorted order, if possible """
        return list(self._dict.keys())

    def extend(self, args):
        """ Add several items at once. """
        for arg in args:
            self.add(arg)

    def add(self, item):
        """Add one item to set"""
        self._dict[item] = item

    def remove(self, item):
        """Remove item from set
        this will raise a KeyError if item doesn't exist
        """
        del self._dict[item]

    def discard(self, item):
        """Removes an item for set
        Doesn't raise error if item doesn't exist
        """
        if item in self._dict:
            self.remove(item)

    def contains(self, item):
        """Check if the set contains item"""
        return item in self._dict

    def get(self, item):
        """returns the object matching the value of the item"""
        return self._dict.get(item, None)

    @property
    def first(self):
        return self.items[0]

    @property
    def last(self):
        return self.items[len(self.items) - 1]

    def union(self, s2):
        result = copy.copy(self)
        for item in s2:
            result.add(item)
        return result

    # High-performance membership test
    __contains__ = contains

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __getitem__(self, index):
        """ Support the 'for item in set:' protocol. """
        return list(self._dict.keys())[index]

    def __iter__(self):
        """ convert to list """
        return iter(self._dict.copy())

    def __len__(self):
        return len(self._dict)

    def __copy__(self):
        return BetterSet(*self.items)
