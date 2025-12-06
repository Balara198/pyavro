from typing import Dict, List, Tuple, Iterator, Generic, Union, TypeAlias, TypeVar
from collections.abc import MutableMapping

class JsonNull:
    ...

JSON_UNSEEN = object()

JsonNode: TypeAlias = Union[
    None,
    JsonNull,
    str,
    int,
    float,
    bool,
    List["JsonNode"],
    Dict[str, "JsonNode"]
]


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class IdentityDict(MutableMapping[K, V], Generic[K, V]):
    """
    Identity-based mapping: keys are compared by K identity (is), not equality (==).
    Strong references are kept to keys to avoid id reuse issues.
    """
    def __init__(self) -> None:
        self._data: dict[int, tuple[K, V]] = {}

    def __setitem__(self, key: K, value: V) -> None:
        self._data[id(key)] = (key, value)

    def __getitem__(self, key: K) -> V:
        return self._data[id(key)][1]

    def __delitem__(self, key: K) -> None:
        del self._data[id(key)]

    def __contains__(self, key: K) -> bool:  # identity semantics
        return id(key) in self._data

    def __iter__(self) -> Iterator[K]:
        # iterate original keys
        for k, _ in self._data.values():
            yield k

    def __len__(self) -> int:
        return len(self._data)

    # Helpful dict-like APIs
    def get(self, key: K, default: V | None = None) -> V:
        entry = self._data.get(id(key))
        return entry[1] if entry is not None else default

    def pop(self, key: K, default: V | None = None) -> V:
        iid = id(key)
        if iid in self._data:
            _, value = self._data.pop(iid)
            return value
        if default is not None:
            return default
        raise KeyError(key)

    def clear(self) -> None:
        self._data.clear()

    def items(self) -> Iterator[Tuple[K, V]]:
        for k, v in self._data.values():
            yield (k, v)

    def keys(self) -> Iterator[K]:
        for k, _ in self._data.values():
            yield k

    def values(self) -> Iterator[V]:
        for _, v in self._data.values():
            yield v

    # Optional: equality semantics similar to IdentityHashMap (compare entries by key identity)
    def __eq__(self, other: K) -> bool:
        if not isinstance(other, IdentityDict):
            return NotImplemented
        # Compare by identity of keys and equality of values
        if len(self) != len(other):
            return False
        # Build a map of id(key) -> value for the other dict
        other_map = {id(k): v for k, v in other.items()}
        for k, v in self.items():
            ov = other_map.get(id(k), Ellipsis)
            if ov is Ellipsis or ov != v:
                return False
        return True

def require_not_none(value: T, message = "Null pointer exception") -> T:
    if value is None:
        raise ValueError(message)
    return value