"""More collections"""


from itertools import chain
from collections import UserDict


class Otom(UserDict):
    """A One-To-One Mapping between two non-overlapping sets of value,
    acting like a dict, feeling like a dict, but raising much more errors than a dict"""

    def __init__(self, *args, **kwargs):
        self.__keyset = set()  # will be populated by super.__init__ call via update() method
        super().__init__(*args, **kwargs)
        # keep information of initial keys and values for each pair
        assert self.__ensure_otom()  # ignore that call when not debugging

    def __ensure_otom(self):
        "Raises errors if the mapping is not a one-to-one mapping"
        for k, v in self.data.items():
            if v not in self.data:
                raise ValueError(f"Key {repr(k)} is associated to value {repr(v)}, but {repr(v)} is not present as key.")
            if self.data[v] != k:
                raise ValueError(f"Key {repr(k)} is associated to value {repr(v)}, but {repr(v)} is associated to {repr(self.data[v])}.")
        return True


    def __iter__(self):
        "Yield keys that belong to the initial keyset"
        yield from self.__keyset

    def __len__(self):
        "Length is not the number of keys, but the size of the two sets"
        return len(self.__keyset)

    def allkeys(self):
        yield from chain(self, self.values())

    def __eq__(self, othr: dict):
        return self.data == othr.data

    def __setitem__(self, key, val):
        # remove old association val->key if it exists
        if key in self.data:
            oldval = self.data[key]
            assert oldval in self.data  # because its a one to one mapping, the old value should also be a key
            del self.data[oldval]
            if oldval in self.__keyset:  # meaning the "real" key is the given value
                self.__keyset -= {oldval}  # maintain the internal keyset
                self.__keyset |= {val}
        if not self.__keyset & {key, val}:  # new values were added
            self.__keyset.add(key)
        # create the new key->val, and the new val->key
        super().__setitem__(key, val)
        super().__setitem__(val, key)
        # fail on error
        self.__ensure_otom()

    def __delitem__(self, key):
        # also remove the reverse association
        if key in self.data:
            val = self.data[key]
            self.__keyset -= {key, val}
            super().__delitem__(val)
        super().__delitem__(key)

    def __repr__(self):
        return f'Otom({super().__repr__()})'

    def __str__(self):
        return f'Otom({super().__str__()})'
