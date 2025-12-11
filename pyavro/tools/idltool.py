from pathlib import Path
from typing import Optional, TextIO

from pyavro.idl.idlreader import IdlReader


class IdlTool:
    def run(input_stream: TextIO, output_stream: TextIO, error_stream: TextIO, input_dir: Optional[Path]):
        parser = IdlReader()
        idl_file = parser.parse(input_stream, input_dir)
        for warning in idl_file.warnings:
            error_stream.write(warning)
        m = idl_file.main_schema
        p = idl_file.protocol

        if m is None and p is None:
            raise ValueError("Error: the IDL file does not contain a schema nor a protocol.")
        
        out = str(m) if m is not None else str(p)

        output_stream.write(out)
        
        