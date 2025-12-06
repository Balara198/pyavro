from pathlib import Path
from typing import Callable, Deque, Dict, Optional, Set
import unicodedata
import regex
from antlr4 import CommonTokenStream, FileStream, Token, ParserRuleContext
from antlr4.error.ErrorListener import ErrorListener

from converter.core.Idlexer import IdlLexer
from converter.idlfile import IdlFile
from core.IdlListener import IdlListener
from core.IdlParser import IdlParser

from pyavro import Protocol, Schema, ParseContext, JsonProperties
from pyavro.logicaltype import LogicalType
from pyavro.logicaltypes import LogicalTypes
from pyavro.schema import Field, Type
from pyavro.utils import JsonNode

try:
    from typing import override
except ImportError:
    def override(func):
        return func


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

    WS_INDENT = regex.compile(r'(?V1)(?U).*\R(?<indent>\h*).*(?:\R\k<indent>.*)*', 
                            regex.DOTALL | regex.UNICODE | regex.VERBOSE)
    STAR_INDENT = regex.compile(r'(?V1)(?U)(?<start>\*{1,2}).*(?:\R\h*\k<stars>.*)*',
                                regex.DOTALL | regex.UNICODE, regex.VERBOSE)
    VALID_NAME = regex.compile(r'[_\p{L}][_\p{L}\d]*', regex.UNICODE | regex.V1)

    INVALID_TYPE_NAMES = {"boolean", "int", "long", "float", "double", "bytes", "string", 
                        "null", "date", "time_ms", "timestamp_ms", "localtimestamp_ms", "uuid"}
    NAMED_SCHEMA_TYPES: Set[Type] = {Type.RECORD, Type.ENUM, Type.FIXED}

    def __init__(self, parse_context: Optional[ParseContext] = None):
        self.read_locations: Set[Path] = set()
        self.parse_context = parse_context or ParseContext()

    def named_schema_or_unresolved(self, full_name: str) -> Schema:
        return self.parse_context.find(full_name, None)
    
    def parse(self, location: Path) -> IdlFile:
        # TODO: implement reading from stdin
        self.read_locations.add(location)
        input_dir = location.parent
        
        input_stream = FileStream(location)
        lexer = IdlLexer(input_stream)
        token_stream = CommonTokenStream(lexer)

        parse_listener = self.IdlParserListener(input_dir, token_stream, self.parse_context)

        parser = IdlParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(IdlReader.SIMPLE_AVRO_ERROR_LISTENER)
        parser.addParseListener(parse_listener)
        parser.setTrace(False)
        parser.buildParseTrees = False

        try:
            parser.idlFile()
        except SchemaParseException as e:
            raise e
        except Exception as e:
            raise SchemaParseException(e)
        
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
                     parse_contex: ParseContext):
            self.parse_context = parse_contex

            self.input_dir = input_dir
            self.token_stream = token_stream
            self.hidden_tokens_processed_index: int = -1
            self.warnings: list[str] = []

            self.result: IdlFile = None
            self.main_schema: Schema = None
            self.protocol: Protocol = None
            self.namespaces: Deque[str] = Deque()
            self.enum_symbols: list[str] = []
            self.enum_default_symbol: str = None
            self.schema: Schema = None
            self.default_variable_doc_comment: str = None
            self.fields: list[Field] = []
            self.type_stack: Deque[Schema] = Deque()
            self.properties_stack: Deque[IdlReader.SchemaProperties]
            self.json_values = Deque()
        
        def get_idl_file(self) -> IdlFile:
            return self.result

        def get_doc_comment(self, ctx: ParserRuleContext) -> str:
            new_hidden_tokens_processed_index: int = ctx.start.start
            doc_comment_tokens: list[Token] = self.token_stream.getHiddenTokensToLeft(new_hidden_tokens_processed_index, -1)
            search_end_index: int = new_hidden_tokens_processed_index

            doc_comment_token: Token = None
            if doc_comment_tokens is not None:
                doc_comment_token = doc_comment_tokens[-1]
                search_end_index = doc_comment_token.tokenIndex -1

            all_hidden_tokens: set[Token] = frozenset([IdlParser.DocComment])
            if search_end_index > 0:
                hidden_tokens: list[Token] = self.token_stream.getTokens(self.hidden_tokens_processed_index + 1,
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
            self.namespaces.appendleft("" if namespace is None else namespace)

        def current_namespace(self) -> str:
            namespace: str = None if len(self.namespaces) else self.namespaces[-1]
            return None if namespace in [None, ""] else namespace

        def pop_namespace(self):
            self.namespaces.pop()
        
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
            main_schema = self.type_stack.pop()

            if (main_schema.type in IdlReader.NAMED_SCHEMA_TYPES):
                self.parse_context.put(main_schema)

            assert len(self.type_stack) == 0
        
        @override
        def enterSchemaProperty(self, ctx: IdlParser.SchemaPropertyContext):
            assert len(self.json_values) == 0

        @override
        def exitSchemaProperty(self, ctx: IdlParser.SchemaPropertyContext):
            name: str = self.identifier(ctx.name)
            value: JsonNode = self.json_values.pop()
            first_token: Token = ctx.value.start

            self.properties_stack[0].add_property(name, value, first_token)
            super().exitSchemaProperty(ctx)


        @override
        def exitImportStatement(self, ctx: IdlParser.ImportStatementContext):
            import_file = self.get_string(ctx.location)
            raise NotImplementedError()
        
        @override
        def enterFixedDeclaration(self, ctx: IdlParser.FieldDeclarationContext):
            self.properties_stack.appendleft()

        @override
        def exitJsonValue(self, ctx: IdlParser.JsonValueContext):
            if isinstance(ctx.parentCtx, IdlParser.JsonArrayContext):
                value = self.json_values.popleft()
                assert isinstance(self.json_values[0], list)
                self.json_values[0].append(value)

        @override
        def exitJsonLiteral(self, ctx: IdlParser.JsonLiteralContext):
            literal: Token = ctx.literal
            match literal.type:
                case IdlParser.Null:
                    self.json_values.appendleft(None)
                case IdlParser.BTrue:
                    self.json_values.appendleft(True)
                case IdlParser.BFalse:
                    self.json_values.appendleft(False)
                case IdlParser.IntegerLiteral:
                    number: str = literal.text.replace("_", "")
                    last_char = number[-1]
                    if (last_char in 'lL'):
                        number = number[:-1]
                    int_number = int(number)
                    self.json_values.appendleft(int_number)
                case IdlParser.FloatingPointLiteral:
                    self.json_values.appendleft(float(literal.text))
                case _:
                    self.json_values.appendleft(self.get_string(literal))

        @override
        def enterJsonArray(self, ctx: IdlParser.JsonArrayContext):
            self.json_values.appendleft([])

        @override
        def enterJsonObject(self, ctx: IdlParser.JsonObjectContext):
            self.json_values.appendleft({})

        @override
        def exitJsonPair(self, ctx: IdlParser.JsonPairContext):
            name: str = self.get_string(ctx.name)
            value = self.json_values.popleft()
            assert isinstance(self.json_values[0], dict)
            self.json_values[0][name] = value


        def identifier(self, ctx: IdlParser.IdentifierContext) -> str:
            return ctx.word.getText().replace("`", "")
        
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
        
        def full_name(namespace: str, type_name: str) -> str:
            if '.' in type_name:
                return type_name
            return f'{namespace}.{type_name}' if namespace else type_name

        def get_string(self, string_token: Token):
            string_literal = string_token.text
            return string_literal[1:-1]
        
    class SchemaProperties:
        def __init__(self, context_namespace: str, with_namespace: bool, with_aliases: bool, with_order: bool):
            self.context_namespace = context_namespace
            self.with_namespace = with_namespace
            self._namespace = None
            self.with_aliases = with_aliases
            self.aliases: list[str] = []
            self.with_order = with_order
            self.order: Schema.Field.Order = Schema.Field.Order.ASCENDING
            self.properties: dict = {}

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
                    case Schema.Field.Order.ASCENDING.value:
                        self.order = Schema.Field.Order.ASCENDING
                    case Schema.Field.Order.DESCENDING.value:
                        self.order = Schema.Field.Order.DESCENDING
                    case Schema.Field.Order.IGNORE.value:
                        self.order = Schema.Field.Order.IGNORE
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
                logical_type: LogicalType = LogicalTypes.from_schema(schema, True)
                if logical_type is None:
                    logical_type.add_to_schema(schema)
            return json_properties
        
        def have_properties(self) -> bool:
            return len(self.properties) > 0