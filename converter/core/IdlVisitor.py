# Generated from ./Idl.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .IdlParser import IdlParser
else:
    from IdlParser import IdlParser

# This class defines a complete generic visitor for a parse tree produced by IdlParser.

class IdlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by IdlParser#idlFile.
    def visitIdlFile(self, ctx:IdlParser.IdlFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#protocolDeclaration.
    def visitProtocolDeclaration(self, ctx:IdlParser.ProtocolDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#protocolDeclarationBody.
    def visitProtocolDeclarationBody(self, ctx:IdlParser.ProtocolDeclarationBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namespaceDeclaration.
    def visitNamespaceDeclaration(self, ctx:IdlParser.NamespaceDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#mainSchemaDeclaration.
    def visitMainSchemaDeclaration(self, ctx:IdlParser.MainSchemaDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#identifier.
    def visitIdentifier(self, ctx:IdlParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#schemaProperty.
    def visitSchemaProperty(self, ctx:IdlParser.SchemaPropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#importStatement.
    def visitImportStatement(self, ctx:IdlParser.ImportStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namedSchemaDeclaration.
    def visitNamedSchemaDeclaration(self, ctx:IdlParser.NamedSchemaDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#fixedDeclaration.
    def visitFixedDeclaration(self, ctx:IdlParser.FixedDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enumDeclaration.
    def visitEnumDeclaration(self, ctx:IdlParser.EnumDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enumSymbol.
    def visitEnumSymbol(self, ctx:IdlParser.EnumSymbolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enumDefault.
    def visitEnumDefault(self, ctx:IdlParser.EnumDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#recordDeclaration.
    def visitRecordDeclaration(self, ctx:IdlParser.RecordDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#recordBody.
    def visitRecordBody(self, ctx:IdlParser.RecordBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#fieldDeclaration.
    def visitFieldDeclaration(self, ctx:IdlParser.FieldDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx:IdlParser.VariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#messageDeclaration.
    def visitMessageDeclaration(self, ctx:IdlParser.MessageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#formalParameter.
    def visitFormalParameter(self, ctx:IdlParser.FormalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#resultType.
    def visitResultType(self, ctx:IdlParser.ResultTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#fullType.
    def visitFullType(self, ctx:IdlParser.FullTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#plainType.
    def visitPlainType(self, ctx:IdlParser.PlainTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#nullableType.
    def visitNullableType(self, ctx:IdlParser.NullableTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#primitiveType.
    def visitPrimitiveType(self, ctx:IdlParser.PrimitiveTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#arrayType.
    def visitArrayType(self, ctx:IdlParser.ArrayTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#mapType.
    def visitMapType(self, ctx:IdlParser.MapTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#unionType.
    def visitUnionType(self, ctx:IdlParser.UnionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonValue.
    def visitJsonValue(self, ctx:IdlParser.JsonValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonLiteral.
    def visitJsonLiteral(self, ctx:IdlParser.JsonLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonObject.
    def visitJsonObject(self, ctx:IdlParser.JsonObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonPair.
    def visitJsonPair(self, ctx:IdlParser.JsonPairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#jsonArray.
    def visitJsonArray(self, ctx:IdlParser.JsonArrayContext):
        return self.visitChildren(ctx)



del IdlParser