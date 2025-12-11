from __future__ import annotations
from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, override

from pyavro.pyavro.utils import JsonNode, JsonNull, IdentityDict
from pyavro.pyavro.namevalidator import UTF_VALIDATOR, NameValidator

if TYPE_CHECKING:
    from pyavro.pyavro.logicaltype import LogicalType

from pyavro.pyavro.jsongenerator import JsonGenerator
from pyavro.pyavro.jsonproperties import JsonProperties

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
        if isinstance(value, Type):
            return True
        for _type in Type:
            if value == _type.value:
                return True
        return False

class Schema(JsonProperties):
    SCHEMA_RESERVED: Set[str] = {"doc", "fields", "items", "name", "namespace", "size", "symbols", "values", "type", "aliases"}
    ENUM_RESERVED: Set[str] = {*SCHEMA_RESERVED, "default"}

    def __init__(self, _type: Type):
        super().__init__(reserved = Schema.ENUM_RESERVED if _type == Type.ENUM else Schema.ENUM_RESERVED)
        self.type: Type = _type
        self.logical_type: Optional['LogicalType'] = None

    @staticmethod
    def create(type: Type) -> Schema:
        ''' Create a schema for a primitive type '''
        match type:
            case Type.STRING:
                return StringSchema()
            case Type.BYTES:
                return BytesSchema()
            case Type.INT:
                return IntSchema()
            case Type.LONG:
                return LongSchema()
            case Type.FLOAT:
                return FloatSchema()
            case Type.DOUBLE:
                return DoubleSchema()
            case Type.BOOLEAN:
                return BooleanSchema()
            case Type.NULL:
                return NullSchema()
            case _:
                # TODO: AvroRuntimeException
                raise ValueError(f"Can't create a: {type.value}")
    
    @staticmethod
    def create_record(name: str, doc: str, namespace: str, is_error: bool = False, fields: Optional[List[Field]] = None) -> Schema:
        return RecordSchema(Name(name, namespace), doc, is_error, fields)
    
    @staticmethod
    def create_enum(name: str, doc: str, namespace: str, values: List[str], enum_default: Optional[str] = None) -> Schema:
        return EnumSchema(Name(name, namespace), doc, values, enum_default)
    
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
        return FixedSchema(Name(name, namespace), doc, size)
    
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
        known_names = known_names or set()
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
        return self.equal_cached_hash(other) and self.props_equal(other)
    
    def equal_cached_hash(self, other: Schema) -> bool:
        return True # TODO: implement
    
    FIELD_RESERVED = {"default", "doc", "name", "order", "type", "aliases"}

    def is_nullable(self) -> bool:
        if not isinstance(self, UnionSchema):
            return self.type == Type.NULL
        
        for schema in self.get_types():
            if schema.is_nullable():
                return True
        
        return False
    
    NULL_DEFAULT_VALUE = object()

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

    VALIDATE_NAMES: NameValidator = UTF_VALIDATOR
    
    @staticmethod
    def validate_name(name: str) -> str:
        result: NameValidator.Result = Schema.VALIDATE_NAMES.validate(name)
        if not result.is_ok():
            raise ValueError(result.errors)
        return name
    
    VALIDATE_DEFAULT: bool = True

    @staticmethod
    def validate_default(field_name: str, schema: Schema, default_value: JsonNode) -> JsonNode:
        if Schema.VALIDATE_NAMES and default_value is not None and not schema.is_valid_default(default_value):
            raise ValueError(
                f"Invalid default for field {field_name}: {default_value} not a {schema}"
            )
        return default_value

    def is_valid_default(self, default_value: JsonNode):
        if default_value is None:
            return False
        match self.type:
            case Type.STRING | Type.BYTES | Type.ENUM | Type.FIXED:
                return isinstance(default_value, str)
            case Type.INT | Type.LONG:
                return isinstance(default_value, int)
            case Type.FLOAT | Type.DOUBLE:
                return isinstance(default_value, (int, float))
            case Type.BOOLEAN:
                return isinstance(default_value, bool)
            case Type.NULL:
                return isinstance(default_value, JsonNull)
            case Type.ARRAY:
                if not isinstance(default_value, list):
                    return False
                for element in default_value:
                    if not self.get_element_type().is_valid_default(element):
                        return False
                return True
            case Type.MAP:
                if not isinstance(default_value, dict):
                    return False
                for key, value in default_value.items():
                    if not isinstance(key, str):
                        return False
                    if not self.get_value_type().is_valid_default(value):
                        return False
                return True
            case Type.UNION:
                for schema in self.get_types():
                    if is_valid_value(schema, default_value):
                        return True
                return False
            case Type.RECORD:
                if not isinstance(default_value, dict):
                    return False
                for field in self.get_fields():
                    if not is_valid_value(
                        field.schema,
                        default_value[field.name] if field.name in default_value else field.default_value):
                        return False
                return True
            case _:
                return False
            
def is_valid_value(schema: Schema, value: JsonNode):
    if value is None:
        return False
    if schema.type == Type.UNION:
        for sub in schema.get_types():
            if sub.is_valid_default(value):
                return True
        return False
    else:
        return schema.is_valid_default(value)
        
# TODO: parsers and parsing

def apply_aliases(writer: Schema, reader: Schema) -> Schema:
    if writer == reader:
        return writer
    
    seen: IdentityDict[Schema, Schema] = IdentityDict()
    aliases: Dict[Name, Name] = {}
    field_aliases: Dict[Name, Dict[str, str]] = {}

    get_aliases(reader, seen, aliases, field_aliases)

    if len(aliases) == 0 and len(field_aliases) == 0:
        return writer
    
    seen.clear()
    return _apply_aliases(writer, seen, aliases, field_aliases)

def _apply_aliases(s: Schema, 
                   seen: IdentityDict[Schema, Schema], 
                   aliases: Dict[Name, Name],
                   field_aliases: Dict[Name, Dict[str, str]]) -> Schema:
    name: Optional[Name] = s.name if isinstance(s, NamedSchema) else None
    result: Schema = s

    match s.type:
        case Type.RECORD:
            if s in seen:
                return seen[s]
            if name in aliases:
                name = aliases[name]
            result = Schema.create_record(name.full, s.get_doc(), None, s.is_error())
            seen[s] = result
            new_fields: List[Field] = []
            for f in s.get_fields():
                f_schema = _apply_aliases(f.schema, seen, aliases, field_aliases)
                f_name = get_field_alias(name, f.name, field_aliases)
                new_f = Field(f_name, f_schema, f.doc(), f.default_value, True, f.order)
                new_f.add_all_props(f)
                new_fields.append(new_f)
            result.set_fields(new_fields)
        case Type.ENUM:
            if name in aliases:
                result = Schema.create_enum(
                    aliases[name].full,
                    s.get_doc(),
                    None,
                    s.get_enum_symbols(),
                    s.get_enum_default())
        case Type.ARRAY:
            e = _apply_aliases(s.get_element_type(), seen, aliases, field_aliases)
            if e != s.get_element_type():
                result = Schema.create_array(e)
        case Type.MAP:
            v = _apply_aliases(s.get_value_type(), seen, aliases, field_aliases)
            if v != s.get_value_type():
                return Schema.create_map(v)
        case Type.UNION:
            types: List[Schema] = []
            for branch in s.get_types():
                types.append(_apply_aliases(branch, seen, aliases, field_aliases))
            result = Schema.create_union(types)
        case Type.FIXED:
            if name in aliases:
                result = Schema.create_fixed(aliases[name].full, s.get_doc(), None, s.get_fixed_size())
        
    if result != s:
        result.add_all_props(s)
    return result

def get_aliases(schema: Schema, 
                seen: IdentityDict[Schema, Schema], 
                aliases: Dict[Name, Name], 
                field_aliases: Dict[Name, Dict[str, str]]):
    if isinstance(schema, NamedSchema):
        if schema.aliases is not None:
            for alias in schema.aliases:
                aliases[alias] = schema.name
    match schema.type:
        case Type.RECORD:
            if schema in seen:
                return
            seen[schema] = schema
            for field in schema.get_fields():
                if field.aliases is None:
                    for field_alias in field.aliases:
                        record_aliases: Dict[str, str] = field_aliases.setdefault(schema.name, {})
                        record_aliases[field_alias] = field.name
                get_aliases(field.schema, seen, aliases, field_aliases)
            if schema.aliases is not None and schema.name in field_aliases:
                for record_alias in schema.aliases:
                    field_aliases[record_alias] = field_aliases[schema.name]
        case Type.ARRAY:
            get_aliases(schema.get_element_type(), seen, aliases, field_aliases)
        case Type.MAP:
            get_aliases(schema.get_value_type(), seen, aliases, field_aliases)
        case Type.UNION:
            for s in schema.get_types():
                get_aliases(s, seen, aliases, field_aliases)

def get_field_alias(record: Name, field: str, field_aliases: Dict[Name, Dict[str, str]]) -> str:
    record_aliases: Dict[str, str] = field_aliases.get(record)
    if record_aliases is None:
        return field
    alias = record_aliases.get(field)
    if alias is None:
        return field
    return alias

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
        if not isinstance(other, Name):
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
            if self.name in Type:
                return True
            return False
        return True

class Field(JsonProperties):
        
    class Order(Enum):
        ASCENDING = "ascending"
        DESCENDING = "descending"
        IGNORE = "ignore"

    def __init__(self, name: str, 
                    schema: Schema, 
                    doc: Optional[str] = None, 
                    default_value: JsonNode = None, 
                    validate_default: bool = True, 
                    order: Order = Order.ASCENDING):
        super().__init__(Schema.FIELD_RESERVED)
        self.name = Schema.validate_name(name)
        self.schema = schema
        self.doc = doc
        self.default_value: JsonNode = Schema.validate_default(name, schema, default_value) if validate_default else default_value
        self.order = order
        self._aliases: Set[str] = None
        self.position = -1

    @staticmethod
    def create(field: Field, schema: Schema) -> Field:
        new_field = Field(
            field.name,
            schema, 
            field.doc, 
            field.default_value, 
            True,
            field.order)
        new_field.add_all_props(field)
        if field._aliases != None:
            new_field._aliases = field._aliases.copy()
        return new_field
    
    def has_default_value(self) -> bool:
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
        if not isinstance(other, Field):
            return False
        return (self.name == other.name and 
                self.schema == other.schema and 
                self.default_value == other.default_value and
                self.order == other.order and 
                self.props_equal(other))
    
    @override
    def __str__(self):
        return f'{self.name} type: {self.schema.type} pos: {self.position}'

class NamedSchema(Schema, ABC):
    def __init__(self, _type: Type, name: Name, doc: str):
        super().__init__(_type)
        self.name = name
        self.doc = doc
        self.aliases: Set[Name] = set()
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
        self.aliases.add(Name(name, namespace))

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
            if self.name.full in known_names:
                gen.write_string(self.name.get_qualified(current_namespace))
                return True
            known_names.add(self.name.full)
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
    def __init__(self, name: Name, doc: str, is_error: bool, fields: Optional[List[Field]] = None):
        super().__init__(Type.RECORD, name, doc)
        self._is_error = is_error
        self.fields: List[Field] = None
        self.field_map: Dict[str, Field] = None
        if fields is not None:
            self.set_fields(fields)

    @override
    def is_error(self):
        return self._is_error
    
    @override
    def get_field(self, field_name: str) -> Dict[str, Field]:
        if self.field_map is None:
            raise ValueError("Schema fields not set yet")
        return self.field_map.get(field_name)
    
    @override
    def get_fields(self) -> List[Field]:
        if self.fields is None:
            raise ValueError("Schema fields not set yet")
        return self.fields
        
    @override
    def has_fields(self):
        return self.fields is not None
    
    @override
    def set_fields(self, fields: List[Field]):
        if self.fields is not None:
            raise ValueError("Fields are already set")
        self.field_map = {}
        self.fields = []
        for i, field in enumerate(fields):
            if field.position != -1:
                raise ValueError(f"Field already used: {field}")
            field.position = i
            if field.name in self.field_map:
                existing_field = self.field_map[field.name]
                raise ValueError(f"Duplicate field {field.name} in record {self.name}: {field} and {existing_field}")
            self.field_map[field.name] = field
            self.fields.append(field)

    @override
    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, RecordSchema):
            return False
        if not self.equal_cached_hash(other):
            return False
        if not self.equal_names(other):
            return False
        if not self.props_equal(other):
            return False
        seen: Set[SeenPair] = self.SEEN_EQUALS
        here = SeenPair(self, other)
        if here in seen:
            return True
        first: bool = len(seen) == 0
        seen.add(here)
        ret = self.fields == other.fields
        if first:
            seen.clear()
        return ret
    
    # TODO: ComputeHash?

    @override
    def to_json(self, known_names: Set[str], current_namespace: str, gen: JsonGenerator):
        if self.write_name_ref(known_names, current_namespace, gen):
            return
        gen.write_start_object()
        gen.write_string_field("type", "error" if self.is_error() else "record")
        self.write_name(current_namespace, gen)
        if self.get_doc() is not None:
            gen.write_string_field("doc", self.get_doc())
        
        if self.fields is not None:
            gen.write_field_name("fields")
            self.fields_to_json(known_names, self.name.namespace, gen)
        
        self.write_props(gen)
        self.aliases_to_json(gen)
        gen.write_end_object()

    @override
    def fields_to_json(self, known_names: Set[str], namespace: str, gen: JsonGenerator):
        gen.write_start_array()
        for field in self.fields:
            gen.write_start_object()
            gen.write_string_field("name", field.name)
            gen.write_field_name("type")
            field.schema.to_json(known_names, namespace, gen)
            if field.doc is not None:
                gen.write_string_field("doc", field.doc)
            if field.has_default_value():
                gen.write_field_name("default")
                gen.write_tree(field.default_value)
            if field.order != Field.Order.ASCENDING:
                gen.write_string_field("order", field.order.value)
            if field.aliases is not None and len(self.aliases) > 0:
                gen.write_field_name("aliases")
                gen.write_start_array()
                for alias in self.aliases:
                    gen.write_string(alias)
                gen.write_end_array()
            field.write_props(gen)
            gen.write_end_object()
        gen.write_end_array()

class EnumSchema(NamedSchema):
    def __init__(self, name: Name, doc: str, symbols: List[str], enum_default: str):
        super().__init__(Type.ENUM, name, doc)
        self.symbols = symbols
        self.ordinals: Dict[str, int] = {}
        self.enum_default = enum_default
        for i, symbol in enumerate(symbols):
            validated_symbol = self.validate_name(symbol)
            if validated_symbol in self.ordinals:
                raise ValueError(f"Duplicate enum symbol: {symbol}")
            self.ordinals[validated_symbol] = i
        if enum_default is not None and enum_default not in symbols:
            raise ValueError(f"The Enum Default: {enum_default} is not in the enum symbol set: {symbols}")
        
    @override
    def get_enum_symbols(self) -> List[str]:
        return self.symbols
    
    @override
    def has_enum_symbol(self, symbol: str) -> bool:
        return symbol in self.ordinals
    
    @override
    def get_enum_ordinal(self, symbol: str) -> int:
        if (ordinal := self.ordinals.get(symbol)) is None:
            raise ValueError(f'enum value "{symbol}" is not in the enum symbol set {self.symbols}')
        return ordinal
    
    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, EnumSchema):
            return False
        return self.equal_cached_hash(other) and self.equal_names(other) and self.symbols == other.symbols and self.props_equal(other)
    
    @override
    def get_enum_default(self) -> str:
        return self.enum_default
    
    @override
    def to_json(self, known_names: Set[str], current_namespace: str, gen: JsonGenerator):
        if self.write_name_ref(known_names, current_namespace, gen):
            return
        gen.write_start_object()
        gen.write_string_field("type", "enum")
        self.write_name(current_namespace, gen)
        if self.get_doc() is not None:
            gen.write_string_field("doc", self.get_doc())
        gen.write_array_field_start("symbols")
        for symbol in self.symbols:
            gen.write_string(symbol)
        gen.write_end_array()
        if self.get_enum_default() is not None:
            gen.write_string_field("default", self.get_enum_default())
        self.write_props(gen)
        self.aliases_to_json(gen)
        gen.write_end_object()

class ArraySchema(Schema):
    def __init__(self, element_type: Schema):
        super().__init__(Type.ARRAY)
        self.element_type = element_type

    @override
    def get_element_type(self) -> Schema:
        return self.element_type
    
    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, ArraySchema):
            return False
        return self.equal_cached_hash(other) and self.element_type == other.element_type and self.props_equal(other)
    
    @override
    def to_json(self, known_names: Set[str], namespace: str, gen: JsonGenerator):
        gen.write_start_object()
        gen.write_string_field("type", "array")
        gen.write_field_name("items")
        self.element_type.to_json(known_names, namespace, gen)
        self.write_props(gen)
        gen.write_end_object()

class MapSchema(Schema):
    def __init__(self, value_type: Schema):
        super().__init__(Type.MAP)
        self.value_type = value_type

    @override
    def get_value_type(self) -> Schema:
        return self.value_type
    
    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, MapSchema):
            return False
        return self.equal_cached_hash(other) and self.value_type == other.value_type and self.props_equal(other)
    
    @override
    def to_json(self, known_names: str, namespace: str, gen: JsonGenerator):
        gen.write_start_object()
        gen.write_string_field("type", "map")
        gen.write_field_name("values")
        self.value_type.to_json(known_names, namespace, gen)
        self.write_props(gen)
        gen.write_end_object()

class UnionSchema(Schema):
    def __init__(self, types: List[Schema]):
        super().__init__(Type.UNION)
        self.index_by_name: Dict[str, int] = {}
        self.types = types
        for i, _type in enumerate(types):
            if _type.type == Type.UNION:
                raise ValueError(f"Nested union: {self}")
            name = _type.get_full_name()
            if name is None:
                raise ValueError(f"Nameless in union: {self}")
            if name in self.index_by_name:
                raise ValueError(f"Duplicate in union: {name}")
            self.index_by_name[name] = i

    def is_valid_default(self, json_value: JsonNode) -> bool:
        for _type in self.types:
            if _type.is_valid_default(json_value):
                return True
        return False
    
    @override
    def get_types(self) -> List[Schema]:
        return self.types
    
    @override
    def get_index_named(self, name: str) -> int:
        return self.index_by_name.get(name)
    
    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UnionSchema):
            return False
        return self.equal_cached_hash(other) and self.types == other.types and self.props_equal(other)
    
    @override
    def add_prop(self, name, value):
        raise ValueError(f"Can't set properties on a union: {self}")
    
    @override
    def to_json(self, known_names: Set[str], namespace: str, gen: JsonGenerator):
        gen.write_start_array()
        for _type in self.types:
            _type.to_json(known_names, namespace, gen)
        gen.write_end_array()

class FixedSchema(NamedSchema):
    def __init__(self, name, doc, size: int):
        super().__init__(Type.FIXED, name, doc)
        self.size = size

    @override
    def get_fixed_size(self):
        return self.size
    
    @override
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, FixedSchema):
            return False
        return self.equal_cached_hash(other) and self.equal_names(other) and self.size == other.size and self.props_equal(other)
    
    @override
    def to_json(self, known_names: List[str], current_namespace: str, gen: JsonGenerator):
        if self.write_name_ref(known_names, current_namespace, gen):
            return
        gen.write_start_object()
        gen.write_string_field("type", "fixed")
        self.write_name(current_namespace, gen)
        if self.doc is not None:
            gen.write_string_field("doc", self.get_doc())
        gen.write_number_field("size", self.size)
        self.write_props(gen)
        self.aliases_to_json(gen)
        gen.write_end_object()
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
        super().__init__(Type.STRING)

class BytesSchema(Schema):
    def __init__(self):
        super().__init__(Type.BYTES)

class IntSchema(Schema):
    def __init__(self):
        super().__init__(Type.INT)

class LongSchema(Schema):
    def __init__(self):
        super().__init__(Type.LONG)

class FloatSchema(Schema):
    def __init__(self):
        super().__init__(Type.FLOAT)

class DoubleSchema(Schema):
    def __init__(self):
        super().__init__(Type.DOUBLE)

class BooleanSchema(Schema):
    def __init__(self):
        super().__init__(Type.BOOLEAN)

class NullSchema(Schema):
    def __init__(self):
        super().__init__(Type.NULL)

class Names(dict):
    def __init__(self, namespace: Optional[str] = None) -> None:
        super().__init__()
        self._namespace: Optional[str] = namespace

    @property
    def namespace(self) -> Optional[str]:
        return self._namespace

    @namespace.setter
    def namespace(self, value: Optional[str]):
        self._namespace = value

    # Java: public Schema get(String o)
    def get_by_string(self, o: str) -> Optional[Schema]:
        primitive = Schema.PRIMITIVES.get(o)
        if primitive is not None:
            return Schema.create(primitive)

        name = Name(o, self._namespace or "")
        if name not in self:
            name = Name(o, "")
        return super().get(name, None)

    # Java: public boolean contains(Schema schema)
    def contains_schema(self, schema: NamedSchema) -> bool:
        return super().get(schema.name) is not None

    def add(self, schema: NamedSchema) -> None:
        self[schema.name] = schema

    # Java: @Override public Schema put(Name name, Schema schema)
    def __setitem__(self, name: Name, schema: NamedSchema):
        if name in self:
            other = super().get(name)
            if other is not None and other != schema:
                raise ValueError(f"Can't redefine: {name}")
            return
        super().__setitem__(name, schema)

    def __getitem__(self, key):
        if isinstance(key, str):
            result = self.get_by_string(key)
            if result is None:
                raise KeyError(key)
            return result
        return super().__getitem__(key)

    

