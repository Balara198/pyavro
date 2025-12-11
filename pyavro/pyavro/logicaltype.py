from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyavro.pyavro.schema import Schema
    


class LogicalType:
    LOGICAL_TYPE_PROP = "logicalType"
    INCOMPATIBLE_PROPS = {"avro.java.string", "java-class", "java-key-class", "java-element-class"}

    def __init__(self, logical_type_name: str):
        self.name = logical_type_name

    def add_to_schema(self, schema: 'Schema') -> 'Schema':
        self.validate(schema)
        schema.add_prop(self.LOGICAL_TYPE_PROP, self.name)
        schema.logical_type = self
        return schema
    
    def validate(self, schema: 'Schema'):
        for incompatible in self.INCOMPATIBLE_PROPS:
            if schema.get_object_prop(incompatible):
                raise ValueError(f'{self.LOGICAL_TYPE_PROP} cannot be used with {incompatible}')
            