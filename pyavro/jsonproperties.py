from typing import Any, Callable, Deque, Optional
from jsongenerator import JsonGenerator
from __future__ import annotations

class JsonProperties:

    def __init__(self, reserved: str[str], prop_map: Optional[dict[str, Any]] = None):
        # self.prop_order: Deque[tuple[str, Any]] = Deque()
        self.reserved = reserved
        self.props = {}
        for key, value in prop_map.items():
            self.props.setdefault(key, value)

    def get_object_prop(self, name):
        return self.props.get(name)
    
    def add_all_props(self, properties: JsonProperties):
        for key, value in properties.props.items():
            self.add_prop(key, value)

    def add_prop(self, name: str, value: Any):
        if name in self.reserved:
            raise ValueError(f"Can't set reserved property: {name}")
        if self.props.setdefault(name, value) != value:
            raise ValueError(f"Can't overwrite property: {name}")
        
    def __contains__(self, key):
        return key in self.props
    
    def __iter__(self):
        return iter(self.props.items())
    
    def __len__(self):
        return len(self.props)
    
    def for_each_property(self, consumer: Callable[[str, Any], None]):
        for key, value in self.props:
            consumer(key, value)

    def write_props(self, gen: JsonGenerator):
        for key, value in self.props.items():
            gen.write_object_field(key, value)
    
    def props_hash_code(self):
        raise NotImplementedError() # TODO: implement this: dicts and lists
    
    def props_equal(self, other: JsonProperties):
        return self.props == other.props