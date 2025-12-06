# Generated from ./Idl.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .IdlParser import IdlParser
else:
    from IdlParser import IdlParser

# This class defines a complete listener for a parse tree produced by IdlParser.
class IdlListener(ParseTreeListener):

    # Enter a parse tree produced by IdlParser#idlFile.
    def enterIdlFile(self, ctx:IdlParser.IdlFileContext):
        pass

    # Exit a parse tree produced by IdlParser#idlFile.
    def exitIdlFile(self, ctx:IdlParser.IdlFileContext):
        pass


    # Enter a parse tree produced by IdlParser#protocolDeclaration.
    def enterProtocolDeclaration(self, ctx:IdlParser.ProtocolDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#protocolDeclaration.
    def exitProtocolDeclaration(self, ctx:IdlParser.ProtocolDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#protocolDeclarationBody.
    def enterProtocolDeclarationBody(self, ctx:IdlParser.ProtocolDeclarationBodyContext):
        pass

    # Exit a parse tree produced by IdlParser#protocolDeclarationBody.
    def exitProtocolDeclarationBody(self, ctx:IdlParser.ProtocolDeclarationBodyContext):
        pass


    # Enter a parse tree produced by IdlParser#namespaceDeclaration.
    def enterNamespaceDeclaration(self, ctx:IdlParser.NamespaceDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#namespaceDeclaration.
    def exitNamespaceDeclaration(self, ctx:IdlParser.NamespaceDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#mainSchemaDeclaration.
    def enterMainSchemaDeclaration(self, ctx:IdlParser.MainSchemaDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#mainSchemaDeclaration.
    def exitMainSchemaDeclaration(self, ctx:IdlParser.MainSchemaDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#identifier.
    def enterIdentifier(self, ctx:IdlParser.IdentifierContext):
        pass

    # Exit a parse tree produced by IdlParser#identifier.
    def exitIdentifier(self, ctx:IdlParser.IdentifierContext):
        pass


    # Enter a parse tree produced by IdlParser#schemaProperty.
    def enterSchemaProperty(self, ctx:IdlParser.SchemaPropertyContext):
        pass

    # Exit a parse tree produced by IdlParser#schemaProperty.
    def exitSchemaProperty(self, ctx:IdlParser.SchemaPropertyContext):
        pass


    # Enter a parse tree produced by IdlParser#importStatement.
    def enterImportStatement(self, ctx:IdlParser.ImportStatementContext):
        pass

    # Exit a parse tree produced by IdlParser#importStatement.
    def exitImportStatement(self, ctx:IdlParser.ImportStatementContext):
        pass


    # Enter a parse tree produced by IdlParser#namedSchemaDeclaration.
    def enterNamedSchemaDeclaration(self, ctx:IdlParser.NamedSchemaDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#namedSchemaDeclaration.
    def exitNamedSchemaDeclaration(self, ctx:IdlParser.NamedSchemaDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#fixedDeclaration.
    def enterFixedDeclaration(self, ctx:IdlParser.FixedDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#fixedDeclaration.
    def exitFixedDeclaration(self, ctx:IdlParser.FixedDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#enumDeclaration.
    def enterEnumDeclaration(self, ctx:IdlParser.EnumDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#enumDeclaration.
    def exitEnumDeclaration(self, ctx:IdlParser.EnumDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#enumSymbol.
    def enterEnumSymbol(self, ctx:IdlParser.EnumSymbolContext):
        pass

    # Exit a parse tree produced by IdlParser#enumSymbol.
    def exitEnumSymbol(self, ctx:IdlParser.EnumSymbolContext):
        pass


    # Enter a parse tree produced by IdlParser#enumDefault.
    def enterEnumDefault(self, ctx:IdlParser.EnumDefaultContext):
        pass

    # Exit a parse tree produced by IdlParser#enumDefault.
    def exitEnumDefault(self, ctx:IdlParser.EnumDefaultContext):
        pass


    # Enter a parse tree produced by IdlParser#recordDeclaration.
    def enterRecordDeclaration(self, ctx:IdlParser.RecordDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#recordDeclaration.
    def exitRecordDeclaration(self, ctx:IdlParser.RecordDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#recordBody.
    def enterRecordBody(self, ctx:IdlParser.RecordBodyContext):
        pass

    # Exit a parse tree produced by IdlParser#recordBody.
    def exitRecordBody(self, ctx:IdlParser.RecordBodyContext):
        pass


    # Enter a parse tree produced by IdlParser#fieldDeclaration.
    def enterFieldDeclaration(self, ctx:IdlParser.FieldDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#fieldDeclaration.
    def exitFieldDeclaration(self, ctx:IdlParser.FieldDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:IdlParser.VariableDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:IdlParser.VariableDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#messageDeclaration.
    def enterMessageDeclaration(self, ctx:IdlParser.MessageDeclarationContext):
        pass

    # Exit a parse tree produced by IdlParser#messageDeclaration.
    def exitMessageDeclaration(self, ctx:IdlParser.MessageDeclarationContext):
        pass


    # Enter a parse tree produced by IdlParser#formalParameter.
    def enterFormalParameter(self, ctx:IdlParser.FormalParameterContext):
        pass

    # Exit a parse tree produced by IdlParser#formalParameter.
    def exitFormalParameter(self, ctx:IdlParser.FormalParameterContext):
        pass


    # Enter a parse tree produced by IdlParser#resultType.
    def enterResultType(self, ctx:IdlParser.ResultTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#resultType.
    def exitResultType(self, ctx:IdlParser.ResultTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#fullType.
    def enterFullType(self, ctx:IdlParser.FullTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#fullType.
    def exitFullType(self, ctx:IdlParser.FullTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#plainType.
    def enterPlainType(self, ctx:IdlParser.PlainTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#plainType.
    def exitPlainType(self, ctx:IdlParser.PlainTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#nullableType.
    def enterNullableType(self, ctx:IdlParser.NullableTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#nullableType.
    def exitNullableType(self, ctx:IdlParser.NullableTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#primitiveType.
    def enterPrimitiveType(self, ctx:IdlParser.PrimitiveTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#primitiveType.
    def exitPrimitiveType(self, ctx:IdlParser.PrimitiveTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#arrayType.
    def enterArrayType(self, ctx:IdlParser.ArrayTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#arrayType.
    def exitArrayType(self, ctx:IdlParser.ArrayTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#mapType.
    def enterMapType(self, ctx:IdlParser.MapTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#mapType.
    def exitMapType(self, ctx:IdlParser.MapTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#unionType.
    def enterUnionType(self, ctx:IdlParser.UnionTypeContext):
        pass

    # Exit a parse tree produced by IdlParser#unionType.
    def exitUnionType(self, ctx:IdlParser.UnionTypeContext):
        pass


    # Enter a parse tree produced by IdlParser#jsonValue.
    def enterJsonValue(self, ctx:IdlParser.JsonValueContext):
        pass

    # Exit a parse tree produced by IdlParser#jsonValue.
    def exitJsonValue(self, ctx:IdlParser.JsonValueContext):
        pass


    # Enter a parse tree produced by IdlParser#jsonLiteral.
    def enterJsonLiteral(self, ctx:IdlParser.JsonLiteralContext):
        pass

    # Exit a parse tree produced by IdlParser#jsonLiteral.
    def exitJsonLiteral(self, ctx:IdlParser.JsonLiteralContext):
        pass


    # Enter a parse tree produced by IdlParser#jsonObject.
    def enterJsonObject(self, ctx:IdlParser.JsonObjectContext):
        pass

    # Exit a parse tree produced by IdlParser#jsonObject.
    def exitJsonObject(self, ctx:IdlParser.JsonObjectContext):
        pass


    # Enter a parse tree produced by IdlParser#jsonPair.
    def enterJsonPair(self, ctx:IdlParser.JsonPairContext):
        pass

    # Exit a parse tree produced by IdlParser#jsonPair.
    def exitJsonPair(self, ctx:IdlParser.JsonPairContext):
        pass


    # Enter a parse tree produced by IdlParser#jsonArray.
    def enterJsonArray(self, ctx:IdlParser.JsonArrayContext):
        pass

    # Exit a parse tree produced by IdlParser#jsonArray.
    def exitJsonArray(self, ctx:IdlParser.JsonArrayContext):
        pass



del IdlParser