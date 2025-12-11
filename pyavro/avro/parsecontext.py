from typing import Dict, List, Optional, Set

from pyavro.avro.namevalidator import UTF_VALIDATOR, NameValidator
from pyavro.avro.schema import Schema, Type
from pyavro.avro.util import schemaresolver
from pyavro.avro.util import schemas
from pyavro.avro.utils import require_not_none

class ParseContext:

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

    NAMED_SCHEMA_TYPES: Set[Type] = {Type.RECORD, Type.ENUM, Type.FIXED}



    def __init__(self,
                 name_validator: Optional[NameValidator] = None,
                 old_schemas: Optional[Dict[str, Schema]] = None,
                 new_schemas: Optional[Dict[str, Schema]] = None):
        self.name_validator = name_validator or UTF_VALIDATOR
        self.old_schemas: Dict[str, Schema] = old_schemas or {}
        self.new_schemas: Dict[str, Schema] = new_schemas or {}
        self.resolving_visitor: schemaresolver.ResolvingVisitor = None

    def __contains__(self, name: str):
        return name in self.PRIMITIVES or name in self.old_schemas or name in self.new_schemas

    def find(self, name: str, namespace: Optional[str]) -> Schema:
        _type = self.PRIMITIVES.get(name)
        if _type is not None:
            return Schema.create(_type)
        
        full_name = self.full_name(name, namespace)
        schema = self.get_named_schema(full_name)
        if schema is None:
            schema = self.get_named_schema(name)
        
        return schema if schema is not None else schemaresolver.unresolved_schema(full_name)

    def full_name(self, name: str, namespace: str) -> str:
        if namespace is not None and '.' not in name:
            return f"{namespace}.{name}"
        return name
    
    def get_named_schema(self, full_name: str) -> Optional[Schema]:
        schema = self.old_schemas.get(full_name)
        if schema is None:
            schema = self.new_schemas.get(full_name)
        return schema
    
    def put(self, schema: Schema):
        if schema.type not in self.NAMED_SCHEMA_TYPES:
            raise ValueError("You can only put a named schema into the context")
        
        full_name = self.require_valid_full_name(schema.get_full_name())

        already_known_schema = self.old_schemas.get(full_name)
        if already_known_schema is not None:
            if schema != already_known_schema:
                raise ValueError(f"Can't redefine schema {full_name}")
        else:
            self.resolving_visitor = None
            if self.new_schemas.setdefault(full_name, schema) != schema:
                raise ValueError(f"Can't redefine schema {full_name}")
            
    def require_valid_full_name(self, full_name: str) -> str:
        names = full_name.split('.')
        for name in names[:-1]:
            self.validate_name(name, "Namespace part")
        self.validate_name(names[-1], "Name")
        return full_name
    
    def validate_name(self, name: str, type_of_name: str):
        result: NameValidator.Result = self.name_validator.validate(name)
        if not result.is_ok():
            raise ValueError(f'{type_of_name} "{name}" is invalid: {result.errors}')
        
    def has_new_schemas(self) -> bool:
        return bool(len(self.new_schemas))
    
    def commit(self):
        self.old_schemas.update(self.new_schemas)
        self.new_schemas.clear()

    def rollback(self):
        self.new_schemas.clear()

    def resolve_all_schemas(self) -> List[Schema]:
        self.ensure_schemas_are_resolved()
        return list(self.old_schemas.values())
    
    def ensure_schemas_are_resolved(self):
        if self.has_new_schemas():
            raise ValueError("Schemas cannot be resolved unless the ParseContext is committed.")
        
        if self.resolving_visitor is None:
            saved = Schema.VALIDATE_NAMES
            Schema.VALIDATE_NAMES = self.name_validator
            visitor = schemaresolver.ResolvingVisitor(self.old_schemas.__getitem__)
            for schema in self.old_schemas.values():
                schemas.visit(schema, visitor)
            for name, schema in self.old_schemas.items():
                self.old_schemas[name] = visitor.get_resolved(schema)
            self.resolving_visitor = visitor
            Schema.VALIDATE_NAMES = saved

    def resolve(self, schema: Schema) -> Schema:
        self.ensure_schemas_are_resolved()

        if schema.type in self.NAMED_SCHEMA_TYPES and schema.get_full_name() is not None:
            return require_not_none(self.old_schemas.get(schema.get_full_name()),
                                    f"Unknown schema: {schema.get_full_name()}")
        else:
            schemas.visit(schema, self.resolving_visitor)
            return self.resolving_visitor.get_resolved(schema)
        
    def types_by_name(self) -> Dict[str, Schema]:
        result: Dict[str, Schema] = {}
        result.update(self.old_schemas)
        result.update(self.new_schemas)
        return result