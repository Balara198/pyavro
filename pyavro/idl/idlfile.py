from pathlib import Path
from typing import List, Optional

from pyavro.avro import Protocol, Schema, ParseContext
from pyavro.avro.schema import RecordSchema

class IdlFile:
    def __init__(self, 
                 context: ParseContext,
                 warnings: list[str],
                 main_schema: Optional[Schema] = None, 
                 protocol: Optional[Protocol] = None):
        if main_schema is None and protocol is None:
            raise ValueError("Either of a main_schema or a protocol must be provided")
        self.parse_context: ParseContext = context
        self._named_schemas: dict[str, Schema] = {}
        self._main_schema: Schema = main_schema
        self._protocol: Protocol = protocol
        self.warnings: list[str] = warnings

    def show_new_schemas(self):
        for name, schema in self.parse_context.new_schemas.items():
            if isinstance(schema, RecordSchema):
                print(name, schema.name)

    @property
    def main_schema(self) -> Optional[Schema]:
        if self._main_schema is None:
            return None
        # self.show_new_schemas()
        self.ensure_schemas_are_resolved()
        return self._main_schema
    
    def ensure_schemas_are_resolved(self):
        if self.parse_context is not None:
            self.parse_context.commit()
            schemas: List[Schema] = self.parse_context.resolve_all_schemas()
            for schema in schemas:
                self._named_schemas[schema.get_full_name()] = schema
            if self._main_schema is not None:
                self._main_schema = self.parse_context.resolve(self._main_schema)
            if self.protocol is not None:
                raise NotImplementedError("Protocol handlin not supported yet")
    
    @property
    def protocol(self) -> Optional[Protocol]:
        if self._protocol is None:
            return None
        self.ensure_schemas_are_resolved()
        return self._protocol
    
    def get_warnings(self, import_file: Optional[str] = None) -> list[str]:
        if import_file is None:
            return self.warnings
        return [f'{import_file}  {warning[0].lower()}{warning[1:]}' for warning in self.warnings]
    
    @property
    def named_schemas(self) -> dict[str, Schema]:
        self.ensure_schemas_are_resolved()
        return self._named_schemas
    
    def get_named_schema(self, name: str) -> Optional[Schema]:
        self.ensure_schemas_are_resolved()
        return self._named_schemas.get(name)
    
    def output_string(self) -> str:
        self.ensure_schemas_are_resolved()
        if self._protocol is not None:
            return str(self._protocol)
        if self._main_schema is not None:
            return str(self._main_schema)
        if len(self._named_schemas) == 0:
            return "[]"
        return '[' + ','.join(map(str, self._named_schemas.values())) + ']'
        
        