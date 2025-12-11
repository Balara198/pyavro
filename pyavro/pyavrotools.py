from typing import IO, Optional, TextIO
import click
from pathlib import Path

from pyavro.tools.idltool import IdlTool


@click.group()
def avro_tools():
    ...

@avro_tools.command("idl")
@click.argument("input_stream", required=False, type=click.File("r"), metavar="[IN]")
@click.argument("output_stream", required=False, type=click.File("w"), metavar="[OUT]")
def idl_tool(input_stream: Optional[TextIO],
             output_stream: Optional[TextIO]):

    if input_stream is None:
        input_stream = click.get_text_stream("stdin")
    if output_stream is None:
        output_stream = click.get_text_stream("stdout")
    
    input_path: Path = _resolve_IO_path(input_stream)
    err_stream = click.get_text_stream("stderr")

    IdlTool.run(input_stream, output_stream, err_stream, input_path)

def _resolve_IO_path(stream: IO) -> Optional[Path]:
    name = getattr(stream, "name")
    if name in (None, "-", "<stdin>", "stdin"):
        return None
    try:
        return Path(name).resolve().parent
    except:
        return None