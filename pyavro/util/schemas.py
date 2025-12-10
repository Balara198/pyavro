from typing import Iterable, TypeVar
from pyavro.schema import Schema, Type
from pyavro.util.schemavisitor import SchemaVisitor, SchemaVisitorAction
from pyavro.utils import IdentityDict, Stack

T = TypeVar("T", covariant=True)


def visit(start: Schema, visitor: SchemaVisitor[T]) -> T:
    visited: IdentityDict[Schema, Schema] = IdentityDict()
    dq = Stack()
    dq.push(start)
    while (current := dq.poll()) is not None:
        if callable(current):
            action: SchemaVisitorAction = current()
            match action:
                case SchemaVisitorAction.CONTINUE:
                    pass
                case SchemaVisitorAction.SKIP_SIBLINGS:
                    while isinstance(dq.peek(), Schema):
                        dq.pop()
                case SchemaVisitorAction.TERMINATE:
                    return visitor.get()
                case SchemaVisitorAction.SKIP_SUBTREE | _:
                    raise ValueError(f"Invalid action {action}")
        else:
            schema: Schema = current
            if schema in visited:
                terminate = visit_terminal(visitor, schema, dq)
            else:
                _type = schema.type
                match _type:
                    case Type.ARRAY:
                        terminate = visit_non_terminal(visitor, schema, dq, [schema.get_element_type()])
                        visited[schema] = schema
                    case Type.RECORD:
                        terminate = visit_non_terminal(visitor, schema, dq, reversed([field.schema for field in schema.get_fields()]))
                        visited[schema] = schema
                    case Type.UNION:
                        terminate = visit_non_terminal(visitor, schema, dq, schema.get_types())
                        visited[schema] = schema
                    case Type.MAP:
                        terminate = visit_non_terminal(visitor, schema, dq, [schema.get_value_type()])
                        visited[schema] = schema
                    case _:
                        terminate = visit_terminal(visitor, schema, dq)
            if terminate:
                return visitor.get()
    return visitor.get()


def visit_non_terminal(visitor: SchemaVisitor, schema: Schema, dq: Stack, it_supp: Iterable[Schema]) -> bool:
    action = visitor.visit_non_terminal(schema)
    match action:
        case SchemaVisitorAction.CONTINUE:
            dq.push(lambda: visitor.after_visit_non_terminal(schema))
            for s in it_supp:
                dq.push(s)
        case SchemaVisitorAction.SKIP_SUBTREE:
            dq.push(lambda: visitor.after_visit_non_terminal(schema))
        case SchemaVisitorAction.SKIP_SIBLINGS:
            while isinstance(dq.peek(), Schema):
                dq.pop()
        case SchemaVisitorAction.TERMINATE:
            return True
        case _:
            raise ValueError(f"Invalid action {action} for {schema}")
    return False

def visit_terminal(visitor: SchemaVisitor, schema: Schema, dq: Stack) -> bool:
    action = visitor.visit_terminal(schema)
    match action:
        case SchemaVisitorAction.CONTINUE:
            return False
        case SchemaVisitorAction.SKIP_SIBLINGS:
            while isinstance(dq.peek(), Schema):
                dq.pop()
        case SchemaVisitorAction.TERMINATE:
            return True
        case SchemaVisitorAction.SKIP_SUBTREE | _:
            raise ValueError(f"Invalid action {action} for {schema}")