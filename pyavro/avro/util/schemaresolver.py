from typing import Callable, Set, override

from pyavro.avro.schema import Field, Schema, Type
from pyavro.avro.util import schemas
from pyavro.avro.util.schemavisitor import SchemaVisitor, SchemaVisitorAction
from pyavro.avro.utils import IdentityDict, require_not_none


UR_SCHEMA_ATTR = "org.apache.avro.idl.unresolved.name"
UR_SCHEMA_NAME = "UnresolvedSchema"
UR_SCHEMA_NS = "org.apache.avro.compiler"
COUNTER = 0

def get_and_increment_cnt():
    global COUNTER
    res = COUNTER
    COUNTER += 1
    return res

def unresolved_schema(name: str) -> Schema:
    schema = Schema.create_record(
        f'{UR_SCHEMA_NAME}_{get_and_increment_cnt()}',
        "unresolved schema", UR_SCHEMA_NS, False, [])
    schema.add_prop(UR_SCHEMA_ATTR, name)
    return schema

def is_unresolved_schema(schema: Schema) -> bool:
    return (schema.type == Type.RECORD and 
            schema.get_prop(UR_SCHEMA_ATTR) is not None and
            schema.get_name() is not None and
            schema.get_name().startswith(UR_SCHEMA_NAME) and 
            schema.get_namespace() == UR_SCHEMA_NS)

def get_unresolved_schema_name(schema: Schema) -> str:
    if not is_unresolved_schema(schema):
        raise ValueError(f"Not an unresolved schema: {schema}")
    return schema.get_prop(UR_SCHEMA_ATTR)

def is_fully_resolved_schema(schema: Schema) -> bool:
    if is_unresolved_schema(schema):
        return False
    else:
        return schemas.visit(schema, IsResolvedSchemaVisitor())

class IsResolvedSchemaVisitor(SchemaVisitor[bool]):

    def __init__(self):
        self.has_unresolved_parts: bool = False

    @override
    def visit_terminal(self, terminal: Schema) -> SchemaVisitorAction:
        self.has_unresolved_parts = is_unresolved_schema(terminal)
        return SchemaVisitorAction.TERMINATE if self.has_unresolved_parts else SchemaVisitorAction.CONTINUE

    @override
    def visit_non_terminal(self, non_terminal: Schema) -> SchemaVisitorAction:
        self.has_unresolved_parts = is_unresolved_schema(non_terminal)
        if self.has_unresolved_parts:
            return SchemaVisitorAction.TERMINATE
        if non_terminal.type == Type.RECORD and not non_terminal.has_fields():
            return SchemaVisitorAction.SKIP_SUBTREE
        return SchemaVisitorAction.CONTINUE

    @override
    def after_visit_non_terminal(self, non_terminal: Schema) -> SchemaVisitorAction:
        return SchemaVisitorAction.CONTINUE

    @override
    def get(self) -> bool:
        return not self.has_unresolved_parts

class ResolvingVisitor(SchemaVisitor[None]):
    CONTAINER_SCHEMA_TYPES: Set[Type] = {Type.RECORD, Type.ARRAY, Type.MAP, Type.UNION}
    NAMED_SCHEMA_TYPES: Set[Type] = {Type.RECORD, Type.ENUM, Type.FIXED}
    
    def __init__(self, symbol_table: Callable[[str], Schema]):
        self.replace: IdentityDict[Schema, Schema] = IdentityDict()
        self.symbol_table = symbol_table
    
    @override
    def visit_terminal(self, terminal: Schema) -> SchemaVisitorAction:
        _type = terminal.type
        if _type in self.CONTAINER_SCHEMA_TYPES:
            if terminal not in self.replace:
                raise ValueError(f"Schema {terminal} must be already processed")
        else:
            self.replace[terminal] = terminal
        return SchemaVisitorAction.CONTINUE

    @override
    def visit_non_terminal(self, non_terminal: Schema) -> SchemaVisitorAction:
        _type = non_terminal.type
        if _type == Type.RECORD and non_terminal not in self.replace:
            if is_unresolved_schema(non_terminal):
                unresolved_schema_name = get_unresolved_schema_name(non_terminal)
                resolved_schema = self.symbol_table(unresolved_schema_name)
                if resolved_schema is None:
                    raise ValueError(f"Undefined schema : {unresolved_schema_name}")
                
                replacement = self.replace.get(resolved_schema)
                if replacement is None:
                    schemas.visit(resolved_schema, self)
                    replacement = self.replace.get(resolved_schema)
                    self.replace[resolved_schema] = replacement
                self.replace[non_terminal] = replacement
            else:
                self.replace[non_terminal] = Schema.create_record(
                    non_terminal.get_name(), non_terminal.get_doc(), 
                    non_terminal.get_namespace(), non_terminal.is_error()
                )
        return SchemaVisitorAction.CONTINUE
    
    def copy_properties(self, first: Schema, second: Schema):
        if first.logical_type is not None:
            first.logical_type.add_to_schema(second)
        
        if first.type in self.NAMED_SCHEMA_TYPES:
            for alias in first.get_aliases():
                second.add_alias(alias)
        
        second.add_all_props(first)

    @override
    def after_visit_non_terminal(self, non_terminal: Schema) -> SchemaVisitorAction:
        _type = non_terminal.type
        new_schema: Schema = None
        match _type:
            case Type.RECORD:
                if not is_unresolved_schema(non_terminal):
                    new_schema = self.replace.get(non_terminal)
                    if not new_schema.has_fields():
                        fields = non_terminal.get_fields()
                        new_fields = []
                        for field in fields:
                            # new_fields.append(Field(field, self.replace.get(field.schema)))
                            new_fields.append(Field.create(field, self.replace.get(field.schema)))
                        new_schema.set_fields(new_fields)
                        self.copy_properties(non_terminal, new_schema)
                return SchemaVisitorAction.CONTINUE
            case Type.UNION:
                types = non_terminal.get_types()
                new_types = []
                for sch in types:
                    new_types.append(require_not_none(self.replace.get(sch)))
                new_schema = Schema.create_union(new_types)
            case Type.ARRAY:
                new_schema = Schema.create_array(require_not_none(self.replace.get(non_terminal.get_element_type())))
            case Type.MAP:
                new_schema = Schema.create_map(require_not_none(self.replace.get(non_terminal.get_value_type())))
            case _:
                raise ValueError(f"Illegal type {_type}, schema {non_terminal}")
        self.copy_properties(non_terminal, new_schema)
        self.replace[non_terminal] = new_schema
        return SchemaVisitorAction.CONTINUE
        
    @override
    def get(self):
        return None
    
    def get_resolved(self, schema: Schema) -> Schema:
        return require_not_none(self.replace.get(schema),
                                f"Unknown schema: {schema.get_full_name()}. Was it resolved before?")
    
    def __str__(self):
        return f"ResolvingVisitor{{symbol_table={self.symbol_table}, replace={self.replace}}}"