from typing import Optional, TextIO
from antlr4 import CommonTokenStream
import click

from pyavro.idl.core.IdlLexer import IdlLexer
from pyavro.idl.core.IdlParser import IdlParser

@click.command("lexer")
@click.argument("stream", required=False, type=click.File("r"), metavar="[IN]")
def test_lexer_with_txtio(stream: Optional[TextIO]):
    if stream is None:
        stream = click.get_text_stream("stdin")
    lexer = IdlLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = IdlParser(token_stream, click.get_text_stream('stdout'))
    parser.idlFile()