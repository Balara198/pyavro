from json import JSONEncoder
from typing import Union

class JsonGenerator:
    def __init__(self):
        self.complete = False
        self.initialized = False
        self.result = None
        self.current = []
        self.field_name = None
        self.encoder = JSONEncoder(indent=2)

    def __str__(self):
        if not self.initialized:
            raise ValueError("Cannot convert empty json")
        if self.field_name is not None:
            raise ValueError("Cannot convert json, as the last object value is not set.")
        return self.encoder.encode(self.result)

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

    def write_object_field(self, field_name, value):
        self.write_field_name(field_name)
        self.write(value)
    
    def write(self, value):
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