from typing import Literal
from avro import name, schema, protocol
from antlr4 import FileStream, CommonTokenStream

from core.IdlLexer import IdlLexer
from core.IdlParser import IdlParser

class IdlConversionError(Exception):
    def __init__(self, message, *args):
        self.message = message
        super().__init__(message, *args)

class IdlConverter:
    def __init__(self):
        self.names: name.Names = None
        self.mainSchema: schema.RecordSchema
        self.tree: IdlParser.IdlFileContext

    def parse(self, path: str):
        self.tree = IdlParser(CommonTokenStream(IdlLexer(FileStream(path)))).idlFile()
        if self.tree.mainSchemaDeclaration() is None:
            raise IdlConversionError("No main schema defined")
        self.create_names()
        self.handle_imports()
        self.create_named_type_tree()

    def create_named_type_tree(self):
        '''
        In IDL, a type can be referred before it have been declared.
        But avro library cannot handle that. To add a name to the Names,
        a schema must be provided, which might be a record schema containg
        fields, that might have a named type. If this named type is not
        defined in the Names already, problems might occour. To resolve 
        this, we must add named schemas in the order of reference. 
        Thus we need a tree. 
        '''
        ...
    def create_names(self):
        namespace_declaration: IdlParser.NamespaceDeclarationContext = self.tree.namespaceDeclaration()
        if namespace_declaration is None:
            raise IdlConversionError("No namespace was given")
        namespace = namespace_declaration.namespace.getText()
        self.names = name.Names(default_namespace=namespace)

    def handle_imports(self):
        imports = self.tree.imports
        for _import in imports:
            self.handle_import(_import)

    def handle_import(self, statement: IdlParser.ImportStatementContext):
        import_type: Literal['idl', 'protocol', 'schema'] = statement.importType.text
        import_location: str = statement.location.text.strip('"')
        if '.' not in import_location:
            raise IdlConversionError(f'Cannot import file with no extension: {import_location}')
        inam, iext = import_location.rsplit('.', 1)
        if import_type == 'idl':
            if iext.lower() != 'avdl':
                raise IdlConversionError(f'Not an avdl file: {import_location}')
            ...
        elif import_type == 'schema':
            if iext.lower() != 'avsc':
                raise IdlConversionError(f'Not an avsc file: {import_location}')
            ...
        elif import_type == 'protocol':
            if iext.lower() != 'avpr':
                raise IdlConversionError(f'Not an avpr file: {import_location}')
            raise NotImplementedError('Avro protocol imports are not supported')
        raise NotImplementedError("IDLs with imports are not supported")
            

