from abc import ABC
from enum import Enum
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, override

if TYPE_CHECKING:
    from pyavro.logicaltype import LogicalType

from pyavro.jsongenerator import JsonGenerator
from pyavro.jsonproperties import JsonProperties

class Schema(JsonProperties):

    SCHEMA_RESERVED: Set[str] = {"doc", "fields", "items", "name", "namespace", "size", "symbols", "values", "type", "aliases"}
    ENUM_RESERVED: Set[str] = {*SCHEMA_RESERVED, "default"}

    class Type(Enum):
        RECORD = "record"
        ENUM = "enum"
        ARRAY = "array"
        MAP = "map"
        UNION = "union"
        FIXED = "fixed"
        STRING = "string"
        BYTES = "bytes"
        INT = "int"
        LONG = "long"
        FLOAT = "float"
        DOUBLE = "double"
        BOOLEAN = "boolean"
        NULL = "null"

        def __contains__(value):
            if isinstance(value, Schema.Type):
                return True
            for _type in Schema.Type:
                if value == _type.value:
                    return True
            return False

    def __init__(self, _type: Schema.Type):
        super().__init__(reserved = Schema.ENUM_RESERVED if _type == Schema.Type.ENUM else Schema.ENUM_RESERVED)
        self.type: Schema.Type = _type
        self.logical_type: Optional['LogicalType'] = None

    @staticmethod
    def create(type: Schema.Type) -> Schema:
        ''' Create a schema for a primitive type '''
        match type:
            case Schema.Type.STRING:
                return StringSchema()
            case Schema.Type.BYTES:
                return BytesSchema()
            case Schema.Type.INT:
                return IntSchema()
            case Schema.Type.LONG:
                return LongSchema()
            case Schema.Type.FLOAT:
                return FloatSchema()
            case Schema.Type.DOUBLE:
                return DoubleSchema()
            case Schema.Type.BOOLEAN:
                return BooleanSchema()
            case Schema.Type.NULL:
                return NullSchema()
            case _:
                # TODO: AvroRuntimeException
                raise ValueError(f"Can't create a: {type.value}")
    
    @staticmethod
    def create_record(name: str, doc: str, namespace: str, is_error: bool = False, fields: Optional[List[Field]] = None) -> Schema:
        return RecordSchema(Schema.Name(name, namespace), doc, is_error, fields)
    
    @staticmethod
    def create_enum(name: str, doc: str, namespace: str, values: List[str], enum_default: Optional[List[str]] = None) -> Schema:
        return EnumSchema(Schema.Name(name, namespace), doc, values, enum_default)
    
    @staticmethod
    def create_array(element_type: Schema) -> Schema:
        return ArraySchema(element_type)
    
    @staticmethod
    def create_map(value_type: Schema) -> Schema:
        return MapSchema(value_type)
    
    @staticmethod
    def create_union(types: List[Schema]) -> Schema:
        return UnionSchema(types)
    
    @staticmethod
    def create_fixed(name: str, doc: str, namespace: str, size: int):
        return FixedSchema(Schema.Name(name, namespace), doc, size)
    
    def get_field(self, field_name: str) -> Field:
        raise ValueError(f"Not a record: {self}")
    
    def get_fields(self) -> List[Field]:
        raise ValueError(f"Not a record: {self}")
    
    def has_fields(self) -> bool:
        raise ValueError(f"Not a record: {self}")
    
    def set_fields(self, fields: List[Field]):
        raise ValueError(f"Not a record: {self}")
    
    def get_enum_symbols(self) -> List[str]:
        raise ValueError(f"Not an enum: {self}")
    
    def get_enum_default(self) -> str:
        raise ValueError(f"Not an enum: {self}")
    
    def get_enum_ordinal(self, symbol: str) -> int:
        raise ValueError(f"Not an enum: {self}")
    
    def has_enum_symbol(self, symbol: str) -> bool:
        raise ValueError(f"Not an enum: {self}")
    
    def get_name(self) -> str:
        return self.type.value
    
    def get_doc(self) -> str:
        return None
    
    def get_namespace(self) -> str:
        raise ValueError(f"Not a named type: {self}")
    
    def get_full_name(self) -> str:
        return self.get_name()
    
    def add_alias(self, alias: str, namespace: str):
        raise ValueError(f"Not a named type: {self}")
    
    def get_aliases(self) -> Set[str]:
        raise ValueError(f"Not a named type: {self}")
    
    def is_error(self) -> bool:
        raise ValueError(f"Not a record: {self}")
    
    def get_element_type(self) -> Schema:
        raise ValueError(f"Not an array: {self}")
    
    def get_value_type(self) -> Schema:
        raise ValueError(f"Not a map: {self}")
    
    def get_types(self) -> List[Schema]:
        raise ValueError(f"Not a union: {self}")
    
    def get_index_named(self, name: str) -> int:
        raise ValueError(f"Not a union: {self}")
    
    def get_fixed_size(self) -> int:
        raise ValueError(f"Not fixed: {self}")

    def __str__(self, 
                known_names: Set[str] = None):
        gen = JsonGenerator()
        self.to_json(known_names, None, gen)
        return str(gen)

    def to_json(self, known_names: Set[str], namespace: str, gen: JsonGenerator):
        if len(self.props) == 0:
            gen.write_string(self.get_name())
        else:
            gen.write_start_object()
            gen.write_string_field("type", self.get_name())
            self.write_props(gen)
            gen.write_end_object()
        
    def fields_to_json(self, known_names: Set[str], namespace: str, gen: JsonGenerator):
        raise ValueError(f"Not a record: {self}")
    
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Schema):
            return False
        if self.type != other.type:
            return False
        return self.equals_cached_hash(other) and self.props_equal(other)
    
    def equal_cached_hash(self, other: Schema) -> bool:
        return True # TODO: implement
    
    FIELD_RESERVED = {"default", "doc", "name", "order", "type", "aliases"}

    def is_nullable(self) -> bool:
        if not isinstance(self, UnionSchema):
            return self.type == Schema.Type.NULL
        
        for schema in self.get_types():
            if schema.is_nullable():
                return True
        
        return False
    
    NULL_DEFAULT_VALUE = object()

    class Field(JsonProperties):
        def __init__(self):
            raise NotImplementedError()
        
        class Order(Enum):
            ASCENDING = "ASCENDING"
            DESCENDING = "DESCENDING"
            IGNORE = "IGNORE"

        def __init__(self, name: str, 
                     schema: Schema, 
                     doc: Optional[str] = None, 
                     default_value: Any = None, 
                     validate_default: bool = True, 
                     order: Order = Order.ASCENDING):
            super().__init__(Schema.FIELD_RESERVED)
            self.name = Schema.validate_name(name)
            self.schema = schema
            self.doc = doc
            self.default_value = Schema.validate_default(name, schema, default_value) if validate_default else default_value
            self.order = order
            self._aliases: Set[str] = None
            self.position = -1

        @staticmethod
        def create(field: Schema.Field, schema: Schema) -> Schema.Field:
            new_field = Schema.Field(field.name,
                                     schema, 
                                     field.doc, 
                                     field.default_value, 
                                     True,
                                     field.order)
            new_field.add_all_props(field)
            if field._aliases != None:
                new_field._aliases = field._aliases.copy()
            return new_field
        
        def has_default(self) -> bool:
            return self.default_value is not None
        
        def add_alias(self, alias: str):
            if self._aliases is None:
                self._aliases = set()
            self._aliases.add(alias)

        @property
        def aliases(self):
            if self._aliases == None:
                return set()
            return frozenset(self._aliases)
        
        @override
        def __eq__(self, other):
            if other is self:
                return True
            if not isinstance(other, Schema.Field):
                return False
            return (self.name == other.name and 
                    self.schema == other.schema and 
                    self.default_value == other.default_value and
                    self.order == other.order and 
                    self.props_equal(other))
        
        @override
        def __str__(self):
            return f'{self.name} type: {self.schema.type} pos: {self.position}'


    class Name:
        def __init__(self, name: str, namespace: str):
            self.name: str
            self.namespace: str
            self.full: str
            if name is None:
                self.name = self.namespace = self.full = None
                return
            if '.' not in name:
                self.name = Schema.validate_name(name)
            else:
                namespace, self.name = name.rsplit('.', 1)
                self.name = Schema.validate_name(self.name)
            if namespace == "":
                namespace = None
            self.namespace = namespace
            self.full = self.name if self.namespace is None else f'{self.namespace}.{self.name}'

        def __eq__(self, other):
            if self is other:
                return True
            if not isinstance(other, Schema.Name):
                return False
            return self.full == other.full
        
        def __str__(self):
            return self.full
        
        def write_name(self, current_namespace: str, gen: JsonGenerator):
            # TODO: understand this
            if self.name is not None:
                gen.write_string_field("name", self.name)
            if self.namespace is not None:
                if self.namespace != current_namespace:
                    gen.write_string_field("namespace", self.namespace)
            elif current_namespace is not None:
                gen.write_string_field("namespace", "")
            
        def get_qualified(self, default_namespace: str) -> str:
            return self.full if self.should_write_full(default_namespace) else self.name
        
        def should_write_full(self, default_namespace: str) -> bool:
            if self.namespace is not None and self.namespace == default_namespace:
                if self.name in Schema.Type:
                    return True
                return False
            return True
    
    @staticmethod
    def validate_name(name: str) -> str:
        result: NameValidator.Result = VALIDATE_NAMES.get().validate(name)
        ...

    PRIMITIVES: Dict[str, Type] = {
        "string": Type.STRING,
        "bytes": Type.BYTES,
        "int": Type.INT,
        "long": Type.LONG,
        "float": Type.FLOAT,
        "double": Type.DOUBLE,
        "boolean": Type.BOOLEAN,
        "null": Type.NULL
    }

class NamedSchema(Schema, ABC):
    def __init__(self, _type: Schema.Type, name: Schema.Name, doc: str):
        super().__init__(_type)
        self.name = name
        self.doc = doc
        self.aliases: Set[Schema.Name] = set()
        if self.name.full in self.PRIMITIVES:
            raise ValueError(f"Schemas may not be named after primitives: {self.name.full}")
        
    @override
    def get_name(self):
        return self.name.name
    
    @override
    def get_doc(self):
        return self.doc
    
    @override
    def get_namespace(self):
        return self.name.namespace
    
    @override
    def get_full_name(self):
        return self.name.full
    
    @override
    def add_alias(self, name, namespace: Optional[str] = None):
        if self.aliases is None:
            self.aliases = set()
        if namespace is None:
            namespace = self.name.namespace
        self.aliases.add(Schema.Name(name, namespace))

    @override
    def get_aliases(self) -> Set[str]:
        result = set()
        if self.aliases is not None:
            for alias in self.aliases:
                if alias.namespace is None and self.name.namespace is None:
                    result.add(f".{alias.name}")
                else:
                    result.add(alias.full)
        return result
    
    def write_name_ref(self, known_names: Set[str], current_namespace: str, gen: JsonGenerator):
        if self.name.name is not None:
            if self.name.full not in known_names:
                known_names.add(self.name.full)
                gen.write_string(self.name.get_qualified(current_namespace))
                return True
        return False
    
    def write_name(self, current_namespace: str, gen: JsonGenerator):
        self.name.write_name(current_namespace, gen)

    def equal_names(self, other: NamedSchema) -> bool:
        return self.name == other.name
    
    def aliases_to_json(self, gen: JsonGenerator):
        if self.aliases is None or len(self.aliases) == 0:
            return
        gen.write_field_name("aliases")
        gen.write_start_array()
        for alias in self.aliases:
            gen.write_string(alias.get_qualified(self.name.namespace))
        gen.write_end_array()

    SEEN_EQUALS: Set[SeenPair] = set()

class RecordSchema(NamedSchema):
    def __init__(self, name: Schema.Name, doc: str, is_error: bool, fields: Optional[List[Schema.Field]] = None):
        super().__init__(self.Type.RECORD, name, doc)
        self.is_error = is_error
        self.fields: List[Schema.Field] = None
        self.field_map: Dict[str, Schema.Field]


class SeenPair:
    def __init__(self, s1: Any, s2: Any):
        self.s1 = s1
        self.s2 = s2
    
    def __eq__(self, other):
        if not isinstance(other, SeenPair):
            return False
        return self.s1 == other.s1 and self.s2 == other.s2
                

class StringSchema(Schema):
    def __init__(self):
        super().__init__(self.type.STRING)

class BytesSchema(Schema):
    def __init__(self):
        super().__init__(self.type.BYTES)

class IntSchema(Schema):
    def __init__(self):
        super().__init__(self.type.INT)

class LongSchema(Schema):
    def __init__(self):
        super().__init__(self.type.LONG)

class FloatSchema(Schema):
    def __init__(self):
        super().__init__(self.type.FLOAT)

class DoubleSchema(Schema):
    def __init__(self):
        super().__init__(self.type.DOUBLE)

class BooleanSchema(Schema):
    def __init__(self):
        super().__init__(self.type.BOOLEAN)

class NullSchema(Schema):
    def __init__(self):
        super().__init__(self.type.NULL)
