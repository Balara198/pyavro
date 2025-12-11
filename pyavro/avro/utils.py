from typing import Deque, Dict, List, Tuple, Iterator, Generic, Union, TypeAlias, TypeVar
from collections.abc import MutableMapping

class JsonNull:
    def to_json(self):
        return None

JSON_NULL = JsonNull()
JSON_UNSEEN = object()

JsonNode: TypeAlias = Union[
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

class Stack(Deque[T], Generic[T]):
    """
    Simple stack implementation using Deque as the underlying storage.
    """
    def is_empty(self) -> bool:
        """
        Checks if the stack is empty.

        :return: True if the stack is empty, False otherwise.
        :rtype: bool
        """
        return len(self) == 0
    def push(self, item: T) -> None:
        """
        Pushes an item onto the top of the stack.
        
        :param item: The item to be pushed onto the stack.
        :type item: T
        """
        self.append(item)

    def pop(self) -> T:
        """
        Removes and returns the top item of the stack.

        :return: The top item of the stack.
        :rtype: T
        """
        return super().pop()

    def peek(self) -> T | None:
        """
        Retrieves but does not remove the top item of the stack or returns None if the stack is empty.

        :return: The top item of the stack or None if the stack is empty.
        :rtype: T | None
        """
        return self[-1] if len(self) > 0 else None
    
    def element(self) -> T:
        """
        Retrieves but does not remove the top item of the stack.
        Raises IndexError if the stack is empty.

        :return: The top item of the stack.
        :rtype: T
        """
        if len(self) == 0:
            raise IndexError("Stack is empty")
        return self[-1]
    
    def poll(self) -> T | None:
        """
        Retrieves and removes the top item of the stack or returns None if the stack is empty.

        :return: The top item of the stack or None if the stack is empty.
        :rtype: T | None
        """
        return self.pop() if len(self) > 0 else None
    
    # Other Deque methods are inherited but cannot be used to violate stack semantics.
    def appendleft(self, x):
        raise NotImplementedError("appendleft is not supported in Stack")
    def popleft(self):
        raise NotImplementedError("popleft is not supported in Stack")
    def extendleft(self, iterable):
        raise NotImplementedError("extendleft is not supported in Stack")

def require_not_none(value: T, message = "Null pointer exception") -> T:
    if value is None:
        raise ValueError(message)
    return value