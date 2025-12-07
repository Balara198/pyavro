from typing import Literal, Optional
from avro import name, schema, protocol
from antlr4 import FileStream, CommonTokenStream

from core.Idlexer import IdlLexer
from core.IdlParser import IdlParser

class IdlConversionError(Exception):
    def __init__(self, message, *args):
        self.message = message
        super().__init__(message, *args)

class Name:
    def __init__(self, default_namespace: str, name: str, namespace: Optional[str] = None):
        fully_qualified = '.' in name
        if fully_qualified and namespace:
            raise IdlConversionError('Cannot set namespace while name is already fully qualified.')
        if not default_namespace:
            raise IdlConversionError('Default namespace must be provided for a Name')
        self.name = None
        self.namespace = None
        if fully_qualified:
            self.namespace, self.name = name.rsplit('.', 1)
        else:
            self.name = name
            self.namespace = namespace if namespace else default_namespace
        self.full_name = f'{self.namespace}.{self.name}'


class Names:
    def __init__(self, default_namespace: str):
        self.default_namespace = default_namespace
        self.names = {}
        self.defined: dict[str, dict] = {}
    def add_name(self, name: str, namespace: Optional[str] = None):
        name_obj = Name(self.default_namespace, name, namespace)
        self.names[name_obj.full_name] = name_obj
    def get_name(self, name: str, namespace: Optional[str] = None):
        full_name = Name(self.default_namespace, name, namespace).full_name
        return self.names.get(full_name)
    def set_name_defined(self, schema: dict, name: str, namespace: Optional[str] = None):
        full_name = Name(self.default_namespace, name, namespace)
        self.defined[full_name] = schema


class IdlConverter:
    def __init__(self):
        self.names: Names = None
        self.mainSchema: Name
        self.tree: IdlParser.IdlFileContext