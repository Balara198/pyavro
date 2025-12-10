import inspect
from json import JSONEncoder
from typing import Union

from pyavro.utils import JsonNode

class JsonGenerator:
    def __init__(self):
        self.complete = False
        self.initialized = False
        self.result = None
        self.current = []
        self.field_name = None
        self.encoder = JSONEncoder(default=self.default_to_json)

    def default_to_json(self, o):
        msg = f"Object of type {o.__class__.__name__} is not JSON serializable"
        if not hasattr(o, "to_json"):
            raise TypeError(msg)
        if not callable((to_json := getattr(o, "to_json"))):
            raise TypeError(f'{msg}: to_json must be a method, not an attribute')
        sig = inspect.signature(to_json)
        params = list(sig.parameters.values())

        if len(params) != 0:
                raise TypeError(f'{msg}: expected params for to_json is 0, but was {len(params)}')
        return o.to_json()

    def __str__(self):
        if not self.initialized:
            raise ValueError("Cannot convert empty json")
        if self.field_name is not None:
            raise ValueError("Cannot convert json, as the last object value is not set.")
        return self.encode(self.result, indent_level=2)
    
    def encode(self, x, indent_level=0):
        if isinstance(x, dict):
            items = []
            for k, v in x.items():
                items.append(
                    " " * indent_level + self.encoder.encode(k) + ": " +
                    self.encode(v, indent_level + 2)
                )
            return "{\n" + ",\n".join(items) + "\n" + " " * (indent_level - 2) + "}"
        if isinstance(x, list):
            if any(isinstance(e, dict) for e in x):
                inner = ",\n".join(" " * indent_level + self.encode(e, indent_level + 2) for e in x)
                return "[\n" + inner + "\n" + " " * (indent_level - 2) + "]"
            return self.encoder.encode(x)
        return self.encoder.encode(x)

    @property
    def current_container(self):
        if len(self.current) != 0:
            return self.current[-1]
        else:
            return None

    def write_start_array(self):
        array = []
        if not self.init_result(array):
            self.write(array)
        self.current.append(array)

    def write_end_array(self):
        if not isinstance(self.current_container, list):
            raise ValueError("Cannot end an array, as its not started.")
        self.current.pop()

    def write_start_object(self):
        _object = {}
        if not self.init_result(_object):
            self.write(_object)
        self.current.append(_object)

    def write_end_object(self):
        if not isinstance(self.current_container, dict):
            raise ValueError("Cannot end an object, as its not started.")
        self.current.pop()

    def write_field_name(self, field_name: str):
        if not isinstance(field_name, str):
            raise ValueError("Json object field name must be a string")
        if not isinstance(self.current_container, dict):
            raise ValueError("Cannot write json object field name. Start a json object first")
        if self.field_name is not None:
            raise ValueError("Cannot write json object field name, as the previous field value did not set.")
        self.field_name = field_name

    def write_tree(self, tree):
        self.write(tree)

    def write_string(self, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Cannot write string value of type: {type(value)}")
        self.write(value)
        
    def write_number(self, value: Union[int, float]):
        if not isinstance(value, int) or not isinstance(value, float):
            raise ValueError(f"Cannot write number value of type: {type(value)}")
        self.write(value)
    
    def write_number_field(self, field_name: str, value: Union[int, float]):
        self.write_field_name(field_name)
        self.write_number(value)
        
    def write_string_field(self, field_name: str, value: str):
        self.write_field_name(field_name)
        self.write_string(value)

    def write_array_field_start(self, field_name: str):
        self.write_field_name(field_name)
        self.write_start_array()

    def write_object_field(self, field_name, value: JsonNode):
        self.write_field_name(field_name)
        self.write(value)
    
    def write(self, value: JsonNode):
        if self.complete:
            raise ValueError("Cannot write to json, as its complete")
        if isinstance(self.current_container, dict):
            if self.field_name is None:
                raise ValueError("Cannot write element to json object as no name was specified.")
            self.current_container[self.field_name] = self.validate_value(value)
            self.field_name = None
        elif isinstance(self.current_container, list):
            self.current_container.append(self.validate_value(value))
        else:
            self.result = value
            self.initialized = True
            self.complete = True

    def validate_value(self, value):
        try:
            self.encoder.encode(value)
            return value
        except Exception as e:
            raise e
        
    def init_result(self, element):
        if not self.initialized:
            self.result = element
            self.initialized = True
            return True
        return False