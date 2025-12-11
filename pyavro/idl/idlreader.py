from __future__ import annotations
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, TextIO
import unicodedata
import regex
from antlr4 import CommonTokenStream, InputStream, Token, ParserRuleContext
from antlr4.error.ErrorListener import ErrorListener

from pyavro.idl.core.IdlLexer import IdlLexer
from pyavro.idl.idlfile import IdlFile
from pyavro.idl.core.IdlListener import IdlListener
from pyavro.idl.core.IdlParser import IdlParser

from pyavro.pyavro import Protocol, Schema, ParseContext, JsonProperties
from pyavro.pyavro.logicaltype import LogicalType
from pyavro.pyavro import logicaltypes
from pyavro.pyavro.schema import Field, Type
from pyavro.pyavro.util import schemaresolver
from pyavro.pyavro.utils import JSON_NULL, JsonNode, Stack

try:
    from typing import override
except ImportError:
    def override(func):
        return func


DEBUG = False
def debug(f):
    def wrapper(*args, **kwargs):
        if DEBUG:
            print(f.__name__)
        f(*args, **kwargs)
    return wrapper


class SchemaParseException(Exception):
    def __init__(self, message: str, cause: Exception = None):
        if cause:
            super().__init__(cause)
        else:
            self.message = message
            super().__init__(self.message)

class BaseErrorListener(ErrorListener):
    @override
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SchemaParseException(f"line {line}:{column} {msg}")

class IdlReader:

    SIMPLE_AVRO_ERROR_LISTENER = BaseErrorListener()

    WS_INDENT = regex.compile(r'(?V1).*\R(?P<indent>\h*).*(?:\R(?P=indent).*)*', 
                            regex.DOTALL | regex.UNICODE | regex.VERBOSE)
    STAR_INDENT = regex.compile(r'(?V1)(?P<stars>\*{1,2}).*(?:\R\h*(?P=stars).*)*',
                                regex.DOTALL | regex.UNICODE, regex.VERBOSE)
    VALID_NAME = regex.compile(r'[_\p{L}][_\p{L}\d]*', regex.UNICODE | regex.V1)

    INVALID_TYPE_NAMES = {"boolean", "int", "long", "float", "double", "bytes", "string", 
                        "null", "date", "time_ms", "timestamp_ms", "localtimestamp_ms", "uuid"}
    NAMED_SCHEMA_TYPES: Set[Type] = {Type.RECORD, Type.ENUM, Type.FIXED}

    OPTIONAL_NULLABLE_TYPE_PROPERTY = "org.apache.avro.idl.Idl.NullableType.optional"

    def __init__(self, parse_context: Optional[ParseContext] = None):
        self.read_locations: Set[Path] = set()
        self.parse_context = parse_context or ParseContext()

    def named_schema_or_unresolved(self, full_name: str) -> Schema:
        return self.parse_context.find(full_name, None)
    
    def parse_from_path(self, path: Path):
        with open(path, 'r') as f:
            return self.parse(f, path.parent)

    def parse(self, input_stream: TextIO, input_dir: Optional[Path]) -> IdlFile:
        # TODO: implement reading from stdin
        if input_dir is not None:
            self.read_locations.add(input_dir)
        
        lexer = IdlLexer(InputStream(input_stream.read()))
        token_stream = CommonTokenStream(lexer)

        parse_listener = self.IdlParserListener(input_dir, token_stream, self.parse_context, self)

        parser = IdlParser(token_stream)
        # parser.removeErrorListeners()
        # parser.addErrorListener(IdlReader.SIMPLE_AVRO_ERROR_LISTENER)
        parser.addParseListener(parse_listener)
        # parser.setTrace(False)
        parser.buildParseTrees = True

        # try:
        parser.idlFile()
        # except SchemaParseException as e:
        #     raise e
        # except Exception as e:
        #     raise SchemaParseException(e)
        
        return parse_listener.get_idl_file()
    
    @staticmethod
    def strip_indents(doc_comment: str) -> str:
        star_match = IdlReader.STAR_INDENT.match(doc_comment)
        if star_match:
            stars = regex.escape(star_match.group("stars"))
            pattern = r'(?U)(?:^|(\R)\h*)' + stars + r'\h?'
            return regex.sub(pattern, r'\1', doc_comment)
        return doc_comment
    
    @staticmethod
    def _error(message: str, token: Token, cause: Optional[Exception] = None) -> SchemaParseException:
        exception = SchemaParseException(
            message + ', at line ' + token.line + ", column " + token.column
        )
        # TODO: initcause
        return exception
    
    class IdlParserListener(IdlListener):
        def __init__(self, 
                     input_dir: Path, 
                     token_stream: CommonTokenStream,
                     parse_contex: ParseContext,
                     idl_reader: IdlReader):
            self.idl_reader = idl_reader
            self.parse_context = parse_contex
            self.read_locations = self.idl_reader.read_locations

            self.input_dir = input_dir
            self.token_stream = token_stream
            self.hidden_tokens_processed_index: int = -1
            self.warnings: List[str] = []

            self.result: IdlFile = None
            self.main_schema: Schema = None
            self.protocol: Protocol = None
            self.namespaces: Stack[str] = Stack()
            self.enum_symbols: List[str] = []
            self.enum_default_symbol: str = None
            self.schema: Schema = None
            self.default_variable_doc_comment: str = None
            self.fields: List[Field] = []
            self.type_stack: Stack[Schema] = Stack()
            self.properties_stack: Stack[IdlReader.SchemaProperties] = Stack()
            self.json_values: Stack[JsonNode] = Stack()
            self.message_doc_comment: str = None
        
        def get_idl_file(self) -> IdlFile:
            return self.result

        def get_doc_comment(self, ctx: ParserRuleContext) -> str:
            new_hidden_tokens_processed_index: int = ctx.start.tokenIndex
            doc_comment_tokens: List[Token] = self.token_stream.getHiddenTokensToLeft(new_hidden_tokens_processed_index, -1)
            search_end_index: int = new_hidden_tokens_processed_index

            doc_comment_token: Token = None
            if doc_comment_tokens is not None:
                doc_comment_token = doc_comment_tokens[-1]
                search_end_index = doc_comment_token.tokenIndex -1

            all_hidden_tokens: Set[Token] = frozenset([IdlParser.DocComment])
            if search_end_index > 0:
                hidden_tokens: List[Token] = self.token_stream.getTokens(self.hidden_tokens_processed_index + 1,
                                                                         search_end_index,
                                                                         all_hidden_tokens)
                if hidden_tokens:
                    for token in hidden_tokens:
                        self.warnings.append(f"Line {token.line}, char {token.column + 1}: Ignoring out-of-place documentation comment.\n" + 
                                             f"Did you mean to use a multiline comment ( /* ... */ ) instead?")

            self.hidden_tokens_processed_index = new_hidden_tokens_processed_index

            if doc_comment_token is None:
                return None
            comment = doc_comment_token.text
            text: str = comment[3: -2]               # Strip /** & */
            
            return IdlReader.strip_indents(text.strip())

        def push_namespace(self, namespace: str):
            self.namespaces.push("" if namespace is None else namespace)

        def current_namespace(self) -> str:
            namespace: str = self.namespaces.peek()
            return None if namespace in [None, ""] else namespace

        def pop_namespace(self):
            self.namespaces.pop()

        def enterEveryRule(self, ctx):
            if DEBUG:
                cls_name = ctx.__class__.__name__
                print(f"Enter {cls_name.removesuffix("Context")}")
            return super().enterEveryRule(ctx)
        
        def exitEveryRule(self, ctx):
            if DEBUG:
                cls_name = ctx.__class__.__name__
                print(f"Exit {cls_name.removesuffix("Context")}")
            return super().exitEveryRule(ctx)
        
        @override
        def exitIdlFile(self, ctx: IdlParser.IdlFileContext):
            if self.protocol is None:
                self.result = IdlFile(context=self.parse_context, 
                                      warnings=self.warnings, 
                                      main_schema=self.main_schema)
            else:
                self.result = IdlFile(context=self.parse_context,
                                      warnings=self.warnings,
                                      protocol=self.protocol)
        
        @override
        def enterProtocolDeclaration(self, ctx: IdlParser.ProtocolDeclarationContext):
            raise NotImplementedError('Protocol conversion is not defined')
        
        
        @override
        def enterProtocolDeclarationBody(self, ctx: IdlParser.ProtocolDeclarationBodyContext):
            raise NotImplementedError('Protocol conversion is not defined')

        
        @override
        def exitProtocolDeclaration(self, ctx: IdlParser.ProtocolDeclarationContext):
            raise NotImplementedError('Protocol conversion is not defined')
        
        
        @override
        def exitNamespaceDeclaration(self, ctx: IdlParser.NamespaceDeclarationContext):
            self.push_namespace(self.namespace("", self.identifier(ctx.namespace)))

        
        @override
        def exitMainSchemaDeclaration(self, ctx: IdlParser.MainSchemaDeclarationContext):
            self.main_schema = self.type_stack.pop()

            if (self.main_schema.type in IdlReader.NAMED_SCHEMA_TYPES):
                self.parse_context.put(self.main_schema)

            assert self.type_stack.is_empty()
        
        
        @override
        def enterSchemaProperty(self, ctx: IdlParser.SchemaPropertyContext):
            assert self.json_values.is_empty()

        
        @override
        def exitSchemaProperty(self, ctx: IdlParser.SchemaPropertyContext):
            name: str = self.identifier(ctx.name)
            value: JsonNode = self.json_values.pop()
            first_token: Token = ctx.value.start

            self.properties_stack.element().add_property(name, value, first_token)
            super().exitSchemaProperty(ctx)

        
        @override
        def exitImportStatement(self, ctx: IdlParser.ImportStatementContext):
            import_file = self.get_string(ctx.location)
            import_location: Path = self.find_import(import_file)
            if import_location in self.read_locations:
                return
            self.read_locations.add(import_location)

            match ctx.importType.type:
                case IdlParser.IDL:
                    idl_file = self.idl_reader.parse_from_path(import_location)
                    if (self.protocol is not None and idl_file.protocol is not None):
                        # self.protocol.messages.update(idl_file.protocol.messages)
                        ...
                    self.warnings.extend(idl_file.get_warnings(import_file))
                case IdlParser.Protocol:
                    raise NotImplementedError("Protocols are not yet supported")
                case IdlParser.Schema:
                    raise NotADirectoryError("JsonSchemaParser not implemented yet.")
       
        def find_import(self, import_file: str) -> Path:
            if self.input_dir is None:
                raise ValueError("Cannot import file, as input_dir is None")
            import_location = (self.input_dir / import_file).resolve()
            if not import_location.exists():
                raise FileNotFoundError(f"Cannot import file, as it does not exist: {import_location}")
            return import_location.absolute()
        
        @override
        def enterFixedDeclaration(self, ctx: IdlParser.FixedDeclarationContext):
            self.properties_stack.push(IdlReader.SchemaProperties(
                self.current_namespace(), True, True, False
            ))

        
        @override
        def exitFixedDeclaration(self, ctx: IdlParser.FixedDeclarationContext):
            properties = self.properties_stack.pop()

            doc = self.get_doc_comment(ctx)
            identifier = self.identifier(ctx.name)
            name = self.name(identifier)
            namespace = self.namespace(identifier, properties.namespace)
            size: int = int(ctx.size.text)
            schema = Schema.create_fixed(name, doc, namespace, size)
            properties.copy_aliases(schema.add_alias)
            properties.copy_properties(schema)
            self.parse_context.put(schema)

        
        @override
        def enterEnumDeclaration(self, ctx: IdlParser.EnumDeclarationContext):
            assert len(self.enum_symbols) == 0
            assert self.enum_default_symbol is None
            self.properties_stack.push(IdlReader.SchemaProperties(
                self.current_namespace(), True, True, False
            ))

        
        @override
        def exitEnumDeclaration(self, ctx: IdlParser.EnumDeclarationContext):
            properties = self.properties_stack.pop()

            doc = self.get_doc_comment(ctx)
            identifier = self.identifier(ctx.name)
            name = self.name(identifier)
            namespace = self.namespace(identifier, properties.namespace)

            schema = Schema.create_enum(name, doc, namespace, self.enum_symbols.copy(), self.enum_default_symbol)
            properties.copy_aliases(schema.add_alias)
            properties.copy_properties(schema)

            self.parse_context.put(schema)

            self.enum_symbols.clear()
            self.enum_default_symbol = None

        
        @override
        def enterEnumSymbol(self, ctx: IdlParser.EnumSymbolContext):
            self.properties_stack.push(IdlReader.SchemaProperties(None, False, False, False))

        
        @override
        def exitEnumSymbol(self, ctx: IdlParser.EnumSymbolContext):
            self.properties_stack.pop()
            self.enum_symbols.append(self.identifier(ctx.name))

        
        @override
        def exitEnumDefault(self, ctx: IdlParser.EnumDefaultContext):
            self.enum_default_symbol = self.identifier(ctx.defaultSymbolName)

        
        @override
        def enterRecordDeclaration(self, ctx: IdlParser.RecordDeclarationContext):
            assert self.schema is None
            assert len(self.fields) == 0

            self.properties_stack.push(IdlReader.SchemaProperties(
                self.current_namespace(), True, True, False
            ))

        
        @override
        def enterRecordBody(self, ctx: IdlParser.RecordBodyContext):
            assert len(self.fields) == 0

            record_ctx: IdlParser.RecordDeclarationContext = ctx.parentCtx

            properties = self.properties_stack.pop()

            doc = self.get_doc_comment(record_ctx)
            identifier = self.identifier(record_ctx.name)
            name = self.name(identifier)
            self.push_namespace(self.namespace(identifier, properties.namespace))
            is_error = record_ctx.recordType.type == IdlParser.Error
            self.schema = Schema.create_record(name, doc, self.current_namespace(), is_error)
            properties.copy_aliases(self.schema.add_alias)
            properties.copy_properties(self.schema)

        
        @override
        def exitRecordDeclaration(self, ctx: IdlParser.RecordDeclarationContext):
            self.schema.set_fields(self.fields.copy())
            self.fields.clear()
            self.parse_context.put(self.schema)
            self.schema = None
            self.pop_namespace()

        
        @override
        def enterFieldDeclaration(self, ctx: IdlParser.FieldDeclarationContext):
            assert self.type_stack.is_empty()
            self.default_variable_doc_comment = self.get_doc_comment(ctx)

        
        @override
        def exitFieldDeclaration(self, ctx: IdlParser.FieldDeclarationContext):
            self.type_stack.pop()
            self.default_variable_doc_comment = None

        
        @override
        def enterVariableDeclaration(self, ctx: IdlParser.VariableDeclarationContext):
            assert self.json_values.is_empty()
            self.properties_stack.push(IdlReader.SchemaProperties(self.current_namespace(), False, True, True))

        
        @override
        def exitVariableDeclaration(self, ctx: IdlParser.VariableDeclarationContext):
            doc = self.get_doc_comment(ctx) or self.default_variable_doc_comment
            field_name = self.identifier(ctx.fieldName)

            field_default: JsonNode = self.json_values.poll()
            _type = self.type_stack.element()
            field_type = self.fix_optional_type(_type, field_default)

            properties = self.properties_stack.pop()

            validate = schemaresolver.is_fully_resolved_schema(field_type)
            field = Field(field_name, field_type, doc, field_default, validate, properties.order)
            properties.copy_aliases(field.add_alias)
            properties.copy_properties(field)
            self.fields.append(field)

        def fix_optional_type(self, schema: Schema, default_value: JsonNode) -> Schema:
            optional_type = schema.get_object_prop(IdlReader.OPTIONAL_NULLABLE_TYPE_PROPERTY)
            if optional_type is None:
                return schema
            
            null_schema = schema.get_types()[0]
            non_null_schema = schema.get_types()[1]
            non_null_default = default_value is not None and default_value != JSON_NULL

            if non_null_default:
                return Schema.create_union([non_null_schema, null_schema])
            else:
                return Schema.create_union([null_schema, non_null_schema])
            
        
        @override
        def enterMainSchemaDeclaration(self, ctx):
            return super().enterMainSchemaDeclaration(ctx)

        
        @override
        def enterMessageDeclaration(self, ctx: IdlParser.MessageDeclarationContext):
            assert self.type_stack.is_empty()
            assert len(self.fields) == 0
            assert self.message_doc_comment is None
            self.properties_stack.push(IdlReader.SchemaProperties(self.current_namespace(), False, False, False))
            self.message_doc_comment = self.get_doc_comment(ctx)
        
        
        @override
        def exitMessageDeclaration(self, ctx: IdlParser.MessageDeclarationContext):
            # result_type = self.type_stack.pop()
            # properties = self.properties_stack.pop().properties
            # name = self.identifier(ctx.name)

            # request = Schema.create_record(None, None, None, False, self.fields.copy())
            # self.fields.clear()
            raise NotImplementedError('Protocol conversion is not defined')
        
        
        @override
        def enterFormalParameter(self, ctx: IdlParser.FormalParameterContext):
            assert len(self.type_stack) == 1
            self.default_variable_doc_comment = self.get_doc_comment(ctx)

        
        @override
        def exitFormalParameter(self, ctx: IdlParser.FormalParameterContext):
            self.type_stack.pop()
            self.default_variable_doc_comment = None

        
        @override
        def exitResultType(self, ctx: IdlParser.ResultTypeContext):
            # self.type_stack.pop()
            # self.default_variable_doc_comment = None
            raise NotImplementedError('Protocol conversion is not defined')
        
        
        @override
        def enterFullType(self, ctx: IdlParser.FullTypeContext):
            self.properties_stack.push(IdlReader.SchemaProperties(self.current_namespace(), False, False, False))
            super().enterFullType(ctx)

        
        @override
        def exitFullType(self, ctx: IdlParser.FullTypeContext):
            properties = self.properties_stack.pop()
            _type = self.type_stack.element()

            if _type.get_object_prop(IdlReader.OPTIONAL_NULLABLE_TYPE_PROPERTY) is not None:
                # already optional
                properties.copy_properties(_type.get_types()[1])
            else:
                properties.copy_properties(_type)

        
        @override
        def exitNullableType(self, ctx: IdlParser.NullableTypeContext):
            if ctx.referenceName is None:
                _type = self.type_stack.pop()
            else:
                if self.properties_stack.is_empty() or self.properties_stack.peek().have_properties():
                    raise IdlReader._error("Type references may not be annotated", ctx.parentCtx.start)
                _type = self.idl_reader.named_schema_or_unresolved(
                    self.full_name(self.current_namespace(), self.identifier(ctx.referenceName)))
            if ctx.optional is not None:
                _type = Schema.create_union([Schema.create(Type.NULL), _type])
                _type.add_object_prop(IdlReader.OPTIONAL_NULLABLE_TYPE_PROPERTY, True)
            self.type_stack.push(_type)

        
        @override
        def exitPrimitiveType(self, ctx: IdlParser.PrimitiveTypeContext):
            match ctx.typeName.type:
                case IdlParser.Boolean:
                    self.type_stack.push(Schema.create(Type.BOOLEAN))
                case IdlParser.Int:
                    self.type_stack.push(Schema.create(Type.INT))
                case IdlParser.Long:
                    self.type_stack.push(Schema.create(Type.LONG))
                case IdlParser.Float:
                    self.type_stack.push(Schema.create(Type.FLOAT))
                case IdlParser.Double:
                    self.type_stack.push(Schema.create(Type.DOUBLE))
                case IdlParser.Bytes:
                    self.type_stack.push(Schema.create(Type.BYTES))
                case IdlParser.String:
                    self.type_stack.push(Schema.create(Type.STRING))
                case IdlParser.Null:
                    self.type_stack.push(Schema.create(Type.NULL))
                case IdlParser.Date:
                    self.type_stack.push(logicaltypes.DATE_TYPE.add_to_schema(Schema.create(Type.INT)))
                case IdlParser.Time:
                    self.type_stack.push(logicaltypes.TIME_MILLIS_TYPE.add_to_schema(Schema.create(Type.INT)))
                case IdlParser.Timestamp:
                    self.type_stack.push(logicaltypes.TIMESTAMP_MILLIS_TYPE.add_to_schema(Schema.create(Type.LONG)))
                case IdlParser.LocalTimestamp:
                    self.type_stack.push(logicaltypes.LOCAL_TIMESTAMP_MILLIS_TYPE.add_to_schema(Schema.create(Type.LONG)))
                case IdlParser.UUID:
                    self.type_stack.push(logicaltypes.UUID_TYPE.add_to_schema(Schema.create(Type.STRING)))
                case _: # Only option left: decimal
                    precision = int(ctx.precision.text)
                    scale = int(ctx.scale.text) if ctx.scale is not None else 0
                    self.type_stack.push(logicaltypes.decimal(precision, scale).add_to_schema(Schema.create(Type.BYTES)))
        
        
        @override
        def exitArrayType(self, ctx: IdlParser.ArrayTypeContext):
            self.type_stack.push(Schema.create_array(self.type_stack.pop()))

        
        @override
        def exitMapType(self, ctx: IdlParser.MapTypeContext):
            self.type_stack.push(Schema.create_map(self.type_stack.pop()))

        
        @override
        def enterUnionType(self, ctx: IdlParser.UnionTypeContext):
            self.type_stack.push(Schema.create_union())

        
        @override
        def exitUnionType(self, ctx: IdlParser.UnionTypeContext):
            types: List[Schema] = []
            while (_type := self.type_stack.pop()).type != Type.UNION:
                types.append(_type)
            types.reverse()
            self.type_stack.push(Schema.create_union(types))

        
        @override
        def exitJsonValue(self, ctx: IdlParser.JsonValueContext):
            if isinstance(ctx.parentCtx, IdlParser.JsonArrayContext):
                value = self.json_values.pop()
                assert isinstance(self.json_values.peek(), list)
                self.json_values.element().append(value)

        
        @override
        def exitJsonLiteral(self, ctx: IdlParser.JsonLiteralContext):
            literal: Token = ctx.literal
            match literal.type:
                case IdlParser.Null:
                    self.json_values.push(JSON_NULL)
                case IdlParser.BTrue:
                    self.json_values.push(True)
                case IdlParser.BFalse:
                    self.json_values.push(False)
                case IdlParser.IntegerLiteral:
                    number: str = literal.text.replace("_", "")
                    last_char = number[-1]
                    if (last_char in 'lL'):
                        number = number[:-1]
                    int_number = int(number)
                    self.json_values.push(int_number)
                case IdlParser.FloatingPointLiteral:
                    self.json_values.push(float(literal.text))
                case _:
                    self.json_values.push(self.get_string(literal))

        
        @override
        def enterJsonArray(self, ctx: IdlParser.JsonArrayContext):
            self.json_values.push([])

        
        @override
        def enterJsonObject(self, ctx: IdlParser.JsonObjectContext):
            self.json_values.push({})

        
        @override
        def exitJsonPair(self, ctx: IdlParser.JsonPairContext):
            name: str = self.get_string(ctx.name)
            value = self.json_values.pop()
            assert isinstance(self.json_values.peek(), dict)
            self.json_values.element()[name] = value


        def identifier(self, ctx: IdlParser.IdentifierContext) -> str:
            return ctx.word.text.replace("`", "")
        
        def name(self, identifier: str) -> str:
            return self.validate_name(identifier.rsplit('.', 1)[-1], True)

        def namespace(self, identifier: str, namespace: str) -> str:
            ns = namespace if '.' not in identifier else identifier.rsplit('.', 1)[0]
            if ns is None:
                return None
            for n in ns.split('.'):
                self.validate_name(n, False)
            return ns
        
        def validate_name(self, name: str, is_type_name: bool) -> str:
            if name is None:
                raise SchemaParseException("Name is None")
            normalized = unicodedata.normalize("NFC", name)
            if not IdlReader.VALID_NAME.fullmatch(normalized):
                raise SchemaParseException(f"Illegal name: {name}")
            if is_type_name and name in IdlReader.INVALID_TYPE_NAMES:
                raise SchemaParseException(f"Illegal name: {name}")
            return name
        
        def full_name(self, namespace: str, type_name: str) -> str:
            if '.' in type_name:
                return type_name
            return f'{namespace}.{type_name}' if namespace else type_name

        def get_string(self, string_token: Token) -> str:
            string_literal = string_token.text
            return string_literal[1:-1]
        
    class SchemaProperties:
        def __init__(self, context_namespace: str, with_namespace: bool, with_aliases: bool, with_order: bool):
            self.context_namespace = context_namespace
            self.with_namespace = with_namespace
            self._namespace = None
            self.with_aliases = with_aliases
            self.aliases: List[str] = []
            self.with_order = with_order
            self.order: Field.Order = Field.Order.ASCENDING
            self.properties: Dict = {}

        def add_property(self, name: str, value, first_value_token: Token):
            if self.with_namespace and name == "namespace":
                if not isinstance(value, str):
                    raise IdlReader._error("@namespace(...) must contain a string value", first_value_token)
                else:
                    self._namespace = value
            elif self.with_aliases and name == "aliases":
                if not isinstance(value, list):
                    raise IdlReader._error("@aliases(...) must contain an array of string values", first_value_token)
                if not all(map(lambda v: isinstance(v, str), value)):
                    raise IdlReader._error("@aliases(...) must contain an array of string values", first_value_token)
                self.aliases = value
            elif self.with_order and name == "order":
                if not isinstance(value, str):
                    raise IdlReader._error("@order(...) must contain a string value", first_value_token)
                order_value = value.upper()
                match order_value:
                    case Field.Order.ASCENDING.value:
                        self.order = Field.Order.ASCENDING
                    case Field.Order.DESCENDING.value:
                        self.order = Field.Order.DESCENDING
                    case Field.Order.IGNORE.value:
                        self.order = Field.Order.IGNORE
                    case _:
                        raise IdlReader._error('@order(...) must contain "ASCENDING", "DESCENDING" or "IGNORE"', first_value_token)
            else:
                self.properties[name] = value

        @property
        def namespace(self) -> str:
            return self._namespace or self.context_namespace
        
        def copy_aliases(self, add_alias: Callable[[str], None]):
            for alias in self.aliases:
                add_alias(alias)

        def copy_properties(self, json_properties: JsonProperties) -> JsonProperties:
            for key, value in self.properties.items():
                json_properties.add_prop(key, value)
            if isinstance(json_properties, Schema):
                schema = json_properties
                logical_type: LogicalType = logicaltypes.from_schema(schema, True)
                if logical_type is not None:
                    logical_type.add_to_schema(schema)
            return json_properties
        
        def have_properties(self) -> bool:
            return len(self.properties) > 0