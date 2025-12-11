from __future__ import annotations
from typing import Callable, Optional

from pyavro.pyavro.jsongenerator import JsonGenerator
from pyavro.pyavro.utils import JsonNode

class JsonProperties:

    def __init__(self, reserved: str[str], prop_map: Optional[dict[str, JsonNode]] = None):
        # self.prop_order: Deque[tuple[str, Any]] = Deque()
        self.reserved = reserved
        self.props = {}
        if prop_map is not None:
            for key, value in prop_map.items():
                self.props.setdefault(key, value)

    def get_object_prop(self, name):
        return self.props.get(name)
    
    def add_all_props(self, properties: JsonProperties):
        for key, value in properties.props.items():
            self.add_prop(key, value)

    def add_prop(self, name: str, value: str):
        self.add_object_prop(name, value)
        
    def add_object_prop(self, name: str, value: JsonNode):
        if name in self.reserved:
            raise ValueError(f"Can't set reserved property: {name}")
        if self.props.setdefault(name, value) != value:
            raise ValueError(f"Can't overwrite property: {name}")
        
    def get_prop(self, name: str) -> JsonNode:
        value = self.props.get(name)
        return None if not isinstance(value, str) else value
        
    def __contains__(self, key):
        return key in self.props
    
    def __iter__(self):
        return iter(self.props.items())
    
    def __len__(self):
        return len(self.props)
    
    def for_each_property(self, consumer: Callable[[str, JsonNode], None]):
        for key, value in self.props:
            consumer(key, value)

    def write_props(self, gen: JsonGenerator):
        for key, value in self.props.items():
            gen.write_object_field(key, value)
    
    def props_hash_code(self):
        raise NotImplementedError() # TODO: implement this: dicts and lists
    
    def props_equal(self, other: JsonProperties):
        return self.props == other.props