from typing import Callable, Set, override
from pyavro.schema import Field, Schema, Type
from pyavro.util.schemas import Schemas
from pyavro.util.schemavisitor import SchemaVisitor, SchemaVisitorAction
from pyavro.utils import IdentityDict, require_not_none


class SchemaResolver:
    UR_SCHEMA_ATTR = "org.apache.avro.idl.unresolved.name"
    UR_SCHEMA_NAME = "UnresolvedSchema"
    UR_SCHEMA_NS = "org.apache.avro.compiler"
    COUNTER = 0

    @staticmethod
    def get_and_increment_cnt():
        res = SchemaResolver.COUNTER
        SchemaResolver.COUNTER += 1
        return res

    @staticmethod
    def unresolved_schema(name: str) -> Schema:
        schema = Schema.create_record(
            f'{SchemaResolver.UR_SCHEMA_NAME}_{SchemaResolver.get_and_increment_cnt()}',
            "unresolved schema", SchemaResolver.UR_SCHEMA_NS, False, [])
        schema.add_prop(SchemaResolver.UR_SCHEMA_ATTR, name)
        return schema

def is_unresolved_schema(schema: Schema) -> bool:...
def get_unresolved_schema_name(schema: Schema) -> str:...

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
            if terminal in self.replace:
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
                replacement = self.replace.setdefault(
                    resolved_schema,
                    self.visit_and_replace(resolved_schema))
                self.replace[non_terminal] = replacement
            else:
                self.replace(non_terminal, Schema.create_record(
                    non_terminal.get_name(), non_terminal.get_doc(), 
                    non_terminal.get_namespace(), non_terminal.is_error()
                ))
        return SchemaVisitorAction.CONTINUE
                
                
    def visit_and_replace(self, schema: Schema):
        Schemas.visit(schema, self)
        return self.replace.get(schema)
    
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
                            new_fields.append(Field(field, self.replace.get(field.schema)))
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