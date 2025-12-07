from pathlib import Path
from typing import Optional
from idl.idlreader import IdlReader


class IdlTool:
    def run(input_path: Path, output_path: Optional[Path] = None):
        parser = IdlReader()
        idl_file = parser.parse(input_path)
        for warning in idl_file.warnings:
            print(f"Warning: {warning}")
        m = idl_file.main_schema
        p = idl_file.protocol

        if m is None and p is None:
            raise ValueError("Error: the IDL file does not contain a schema nor a protocol.")
        
        out = str(m) if m is not None else str(p)

        if output_path is None:
            print(out)
        else:
            with open(output_path, 'w') as f:
                f.write(out)
        
        