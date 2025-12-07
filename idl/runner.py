from antlr4 import FileStream, CommonTokenStream

from core.IdlParser import IdlParser
from core.Idlexer import IdlLexer
from core.IdlVisitor import IdlVisitor



class AvdlToAvroVisitor(IdlVisitor):
    def __init__(self):
        self.namespace = None
        self.schema_name = None
        self.types = []

    def visitIdlFile(self, ctx:IdlParser.IdlFileContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        print(ctx.mainSchema.getText())
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#protocolDeclaration.
    def visitProtocolDeclaration(self, ctx:IdlParser.ProtocolDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#protocolDeclarationBody.
    def visitProtocolDeclarationBody(self, ctx:IdlParser.ProtocolDeclarationBodyContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namespaceDeclaration.
    def visitNamespaceDeclaration(self, ctx:IdlParser.NamespaceDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#mainSchemaDeclaration.
    def visitMainSchemaDeclaration(self, ctx:IdlParser.MainSchemaDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#identifier.
    def visitIdentifier(self, ctx:IdlParser.IdentifierContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#schemaProperty.
    def visitSchemaProperty(self, ctx:IdlParser.SchemaPropertyContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#importStatement.
    def visitImportStatement(self, ctx:IdlParser.ImportStatementContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namedSchemaDeclaration.
    def visitNamedSchemaDeclaration(self, ctx:IdlParser.NamedSchemaDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#fixedDeclaration.
    def visitFixedDeclaration(self, ctx:IdlParser.FixedDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enumDeclaration.
    def visitEnumDeclaration(self, ctx:IdlParser.EnumDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enumSymbol.
    def visitEnumSymbol(self, ctx:IdlParser.EnumSymbolContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enumDefault.
    def visitEnumDefault(self, ctx:IdlParser.EnumDefaultContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#recordDeclaration.
    def visitRecordDeclaration(self, ctx:IdlParser.RecordDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#recordBody.
    def visitRecordBody(self, ctx:IdlParser.RecordBodyContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#fieldDeclaration.
    def visitFieldDeclaration(self, ctx:IdlParser.FieldDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx:IdlParser.VariableDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#messageDeclaration.
    def visitMessageDeclaration(self, ctx:IdlParser.MessageDeclarationContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#formalParameter.
    def visitFormalParameter(self, ctx:IdlParser.FormalParameterContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#resultType.
    def visitResultType(self, ctx:IdlParser.ResultTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#fullType.
    def visitFullType(self, ctx:IdlParser.FullTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#plainType.
    def visitPlainType(self, ctx:IdlParser.PlainTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#nullableType.
    def visitNullableType(self, ctx:IdlParser.NullableTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#primitiveType.
    def visitPrimitiveType(self, ctx:IdlParser.PrimitiveTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#arrayType.
    def visitArrayType(self, ctx:IdlParser.ArrayTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#mapType.
    def visitMapType(self, ctx:IdlParser.MapTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#unionType.
    def visitUnionType(self, ctx:IdlParser.UnionTypeContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonValue.
    def visitJsonValue(self, ctx:IdlParser.JsonValueContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonLiteral.
    def visitJsonLiteral(self, ctx:IdlParser.JsonLiteralContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonObject.
    def visitJsonObject(self, ctx:IdlParser.JsonObjectContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonPair.
    def visitJsonPair(self, ctx:IdlParser.JsonPairContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonArray.
    def visitJsonArray(self, ctx:IdlParser.JsonArrayContext):
        # print(ctx)
        # print("\t", ctx.__dict__)
        return self.visitChildren(ctx)


def parse_avdl(path):
    input_stream = FileStream(path)
    lexer = IdlLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = IdlParser(tokens)

    tree = parser.idlFile()
    visistor = AvdlToAvroVisitor()
    visistor.visit(tree)


path = 'testschema.avdl'
tree = parse_avdl(path)