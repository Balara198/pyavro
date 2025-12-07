from antlr4 import CommonTokenStream, FileStream
from idl.core.IdlListener import IdlListener
from idl.core.IdlParser import IdlParser
from idl.core.IdlLexer import IdlLexer

class MyListener(IdlListener):

    # Enter a parse tree produced by IdlParser#idlFile.
    def enterIdlFile(self, ctx:IdlParser.IdlFileContext):
        print("enterIdlFile")

    # Exit a parse tree produced by IdlParser#idlFile.
    def exitIdlFile(self, ctx:IdlParser.IdlFileContext):
        print("exitIdlFile")


    # Enter a parse tree produced by IdlParser#protocolDeclaration.
    def enterProtocolDeclaration(self, ctx:IdlParser.ProtocolDeclarationContext):
        print("enterProtocolDeclaration")

    # Exit a parse tree produced by IdlParser#protocolDeclaration.
    def exitProtocolDeclaration(self, ctx:IdlParser.ProtocolDeclarationContext):
        print("exitProtocolDeclaration")


    # Enter a parse tree produced by IdlParser#protocolDeclarationBody.
    def enterProtocolDeclarationBody(self, ctx:IdlParser.ProtocolDeclarationBodyContext):
        print("enterProtocolDeclarationBody")

    # Exit a parse tree produced by IdlParser#protocolDeclarationBody.
    def exitProtocolDeclarationBody(self, ctx:IdlParser.ProtocolDeclarationBodyContext):
        print("exitProtocolDeclarationBody")


    # Enter a parse tree produced by IdlParser#namespaceDeclaration.
    def enterNamespaceDeclaration(self, ctx:IdlParser.NamespaceDeclarationContext):
        print("enterNamespaceDeclaration")

    # Exit a parse tree produced by IdlParser#namespaceDeclaration.
    def exitNamespaceDeclaration(self, ctx:IdlParser.NamespaceDeclarationContext):
        print("exitNamespaceDeclaration")


    # Enter a parse tree produced by IdlParser#mainSchemaDeclaration.
    def enterMainSchemaDeclaration(self, ctx:IdlParser.MainSchemaDeclarationContext):
        print("enterMainSchemaDeclaration")

    # Exit a parse tree produced by IdlParser#mainSchemaDeclaration.
    def exitMainSchemaDeclaration(self, ctx:IdlParser.MainSchemaDeclarationContext):
        print("exitMainSchemaDeclaration")


    # Enter a parse tree produced by IdlParser#identifier.
    def enterIdentifier(self, ctx:IdlParser.IdentifierContext):
        print("enterIdentifier")

    # Exit a parse tree produced by IdlParser#identifier.
    def exitIdentifier(self, ctx:IdlParser.IdentifierContext):
        print("exitIdentifier")


    # Enter a parse tree produced by IdlParser#schemaProperty.
    def enterSchemaProperty(self, ctx:IdlParser.SchemaPropertyContext):
        print("enterSchemaProperty")

    # Exit a parse tree produced by IdlParser#schemaProperty.
    def exitSchemaProperty(self, ctx:IdlParser.SchemaPropertyContext):
        print("exitSchemaProperty\t\t+1")


    # Enter a parse tree produced by IdlParser#importStatement.
    def enterImportStatement(self, ctx:IdlParser.ImportStatementContext):
        print("enterImportStatement")

    # Exit a parse tree produced by IdlParser#importStatement.
    def exitImportStatement(self, ctx:IdlParser.ImportStatementContext):
        print("exitImportStatement")


    # Enter a parse tree produced by IdlParser#namedSchemaDeclaration.
    def enterNamedSchemaDeclaration(self, ctx:IdlParser.NamedSchemaDeclarationContext):
        print("enterNamedSchemaDeclaration")

    # Exit a parse tree produced by IdlParser#namedSchemaDeclaration.
    def exitNamedSchemaDeclaration(self, ctx:IdlParser.NamedSchemaDeclarationContext):
        print("exitNamedSchemaDeclaration")


    # Enter a parse tree produced by IdlParser#fixedDeclaration.
    def enterFixedDeclaration(self, ctx:IdlParser.FixedDeclarationContext):
        print("enterFixedDeclaration\t\t+1")

    # Exit a parse tree produced by IdlParser#fixedDeclaration.
    def exitFixedDeclaration(self, ctx:IdlParser.FixedDeclarationContext):
        print("exitFixedDeclaration\t\t-1")


    # Enter a parse tree produced by IdlParser#enumDeclaration.
    def enterEnumDeclaration(self, ctx:IdlParser.EnumDeclarationContext):
        print("enterEnumDeclaration\t\t+1")

    # Exit a parse tree produced by IdlParser#enumDeclaration.
    def exitEnumDeclaration(self, ctx:IdlParser.EnumDeclarationContext):
        print("exitEnumDeclaration\t\t-1")


    # Enter a parse tree produced by IdlParser#enumSymbol.
    def enterEnumSymbol(self, ctx:IdlParser.EnumSymbolContext):
        print("enterEnumSymbol\t\t+1")

    # Exit a parse tree produced by IdlParser#enumSymbol.
    def exitEnumSymbol(self, ctx:IdlParser.EnumSymbolContext):
        print("exitEnumSymbol\t\t-1")


    # Enter a parse tree produced by IdlParser#enumDefault.
    def enterEnumDefault(self, ctx:IdlParser.EnumDefaultContext):
        print("enterEnumDefault")

    # Exit a parse tree produced by IdlParser#enumDefault.
    def exitEnumDefault(self, ctx:IdlParser.EnumDefaultContext):
        print("exitEnumDefault")


    # Enter a parse tree produced by IdlParser#recordDeclaration.
    def enterRecordDeclaration(self, ctx:IdlParser.RecordDeclarationContext):
        print("enterRecordDeclaration\t\t+1")

    # Exit a parse tree produced by IdlParser#recordDeclaration.
    def exitRecordDeclaration(self, ctx:IdlParser.RecordDeclarationContext):
        print("exitRecordDeclaration")


    # Enter a parse tree produced by IdlParser#recordBody.
    def enterRecordBody(self, ctx:IdlParser.RecordBodyContext):
        print("enterRecordBody\t\t-1")

    # Exit a parse tree produced by IdlParser#recordBody.
    def exitRecordBody(self, ctx:IdlParser.RecordBodyContext):
        print("exitRecordBody")


    # Enter a parse tree produced by IdlParser#fieldDeclaration.
    def enterFieldDeclaration(self, ctx:IdlParser.FieldDeclarationContext):
        print("enterFieldDeclaration")

    # Exit a parse tree produced by IdlParser#fieldDeclaration.
    def exitFieldDeclaration(self, ctx:IdlParser.FieldDeclarationContext):
        print("exitFieldDeclaration")


    # Enter a parse tree produced by IdlParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:IdlParser.VariableDeclarationContext):
        print("enterVariableDeclaration\t\t+1")

    # Exit a parse tree produced by IdlParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:IdlParser.VariableDeclarationContext):
        print("exitVariableDeclaration\t\t-1")


    # Enter a parse tree produced by IdlParser#messageDeclaration.
    def enterMessageDeclaration(self, ctx:IdlParser.MessageDeclarationContext):
        print("enterMessageDeclaration\t\t+1")

    # Exit a parse tree produced by IdlParser#messageDeclaration.
    def exitMessageDeclaration(self, ctx:IdlParser.MessageDeclarationContext):
        print("exitMessageDeclaration\t\t-1")


    # Enter a parse tree produced by IdlParser#formalParameter.
    def enterFormalParameter(self, ctx:IdlParser.FormalParameterContext):
        print("enterFormalParameter")

    # Exit a parse tree produced by IdlParser#formalParameter.
    def exitFormalParameter(self, ctx:IdlParser.FormalParameterContext):
        print("exitFormalParameter")


    # Enter a parse tree produced by IdlParser#resultType.
    def enterResultType(self, ctx:IdlParser.ResultTypeContext):
        print("enterResultType")

    # Exit a parse tree produced by IdlParser#resultType.
    def exitResultType(self, ctx:IdlParser.ResultTypeContext):
        print("exitResultType")


    # Enter a parse tree produced by IdlParser#fullType.
    def enterFullType(self, ctx:IdlParser.FullTypeContext):
        print("enterFullType\t\t+1")

    # Exit a parse tree produced by IdlParser#fullType.
    def exitFullType(self, ctx:IdlParser.FullTypeContext):
        print("exitFullType\t\t-1")


    # Enter a parse tree produced by IdlParser#plainType.
    def enterPlainType(self, ctx:IdlParser.PlainTypeContext):
        print("enterPlainType")

    # Exit a parse tree produced by IdlParser#plainType.
    def exitPlainType(self, ctx:IdlParser.PlainTypeContext):
        print("exitPlainType")


    # Enter a parse tree produced by IdlParser#nullableType.
    def enterNullableType(self, ctx:IdlParser.NullableTypeContext):
        print("enterNullableType")

    # Exit a parse tree produced by IdlParser#nullableType.
    def exitNullableType(self, ctx:IdlParser.NullableTypeContext):
        print("exitNullableType")


    # Enter a parse tree produced by IdlParser#primitiveType.
    def enterPrimitiveType(self, ctx:IdlParser.PrimitiveTypeContext):
        print("enterPrimitiveType")

    # Exit a parse tree produced by IdlParser#primitiveType.
    def exitPrimitiveType(self, ctx:IdlParser.PrimitiveTypeContext):
        print("exitPrimitiveType")


    # Enter a parse tree produced by IdlParser#arrayType.
    def enterArrayType(self, ctx:IdlParser.ArrayTypeContext):
        print("enterArrayType")

    # Exit a parse tree produced by IdlParser#arrayType.
    def exitArrayType(self, ctx:IdlParser.ArrayTypeContext):
        print("exitArrayType")


    # Enter a parse tree produced by IdlParser#mapType.
    def enterMapType(self, ctx:IdlParser.MapTypeContext):
        print("enterMapType")

    # Exit a parse tree produced by IdlParser#mapType.
    def exitMapType(self, ctx:IdlParser.MapTypeContext):
        print("exitMapType")


    # Enter a parse tree produced by IdlParser#unionType.
    def enterUnionType(self, ctx:IdlParser.UnionTypeContext):
        print("enterUnionType")

    # Exit a parse tree produced by IdlParser#unionType.
    def exitUnionType(self, ctx:IdlParser.UnionTypeContext):
        print("exitUnionType")


    # Enter a parse tree produced by IdlParser#jsonValue.
    def enterJsonValue(self, ctx:IdlParser.JsonValueContext):
        print("enterJsonValue")

    # Exit a parse tree produced by IdlParser#jsonValue.
    def exitJsonValue(self, ctx:IdlParser.JsonValueContext):
        print("exitJsonValue")


    # Enter a parse tree produced by IdlParser#jsonLiteral.
    def enterJsonLiteral(self, ctx:IdlParser.JsonLiteralContext):
        print("enterJsonLiteral")

    # Exit a parse tree produced by IdlParser#jsonLiteral.
    def exitJsonLiteral(self, ctx:IdlParser.JsonLiteralContext):
        print("exitJsonLiteral")


    # Enter a parse tree produced by IdlParser#jsonObject.
    def enterJsonObject(self, ctx:IdlParser.JsonObjectContext):
        print("enterJsonObject")

    # Exit a parse tree produced by IdlParser#jsonObject.
    def exitJsonObject(self, ctx:IdlParser.JsonObjectContext):
        print("exitJsonObject")


    # Enter a parse tree produced by IdlParser#jsonPair.
    def enterJsonPair(self, ctx:IdlParser.JsonPairContext):
        print("enterJsonPair")

    # Exit a parse tree produced by IdlParser#jsonPair.
    def exitJsonPair(self, ctx:IdlParser.JsonPairContext):
        print("exitJsonPair")


    # Enter a parse tree produced by IdlParser#jsonArray.
    def enterJsonArray(self, ctx:IdlParser.JsonArrayContext):
        print("enterJsonArray")

    # Exit a parse tree produced by IdlParser#jsonArray.
    def exitJsonArray(self, ctx:IdlParser.JsonArrayContext):
        print("exitJsonArray")

def run():
    input_stream = FileStream('SimpleSchema.avdl')
    lexer = IdlLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    listener = MyListener()
    parser = IdlParser(token_stream)
    parser.addParseListener(listener)
    parser.buildParseTrees = False
    parser.idlFile()

run()