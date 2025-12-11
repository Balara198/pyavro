from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional, override


class NameValidator(ABC):
    @dataclass(frozen=True)
    class Result:
        errors: Optional[str]

        def is_ok(self) -> bool:
            return self is OK

    def validate(self, name: Optional[str]) -> NameValidator.Result:
        return OK
    
class NoNameValidator(NameValidator):
    ...

class UtfNameValidator(NameValidator):
    @override
    def validate(self, name: Optional[str]) -> NameValidator.Result:
        if name is None:
            return NameValidator.Result("None name")
        if len(name) == 0:
            return NameValidator.Result("Empty name")
        first = name[0]
        if not (first.isalpha() or first == "_"):
            return NameValidator.Result(f"Illegal initial character: {name}")
        for c in name[1:]:
            if not (c.isalnum() or c == "_"):
                return NameValidator.Result(f"Illegal character in: {name}")
        return OK
    
class StrictNameValidator(NameValidator):
    @override
    def validate(self, name: Optional[str]) -> NameValidator.Result:
        if name is None:
            return NameValidator.Result("Null name")
        if len(name) == 0:
            return NameValidator.Result("Empty name")
        first = name[0]
        if not (self._is_letter(first) or first == "_"):
            return NameValidator.Result(f"Illegal initial character: {name}")
        for c in name[1:]:
            if not (self._is_letter(c) or self._is_digit(c) or c == "_"):
                return NameValidator.Result(f"Illegal character in: {name}")
        return OK

    def _is_letter(self, char: str) -> bool:
        return 'a' <= char <= 'z' or 'A' <= char <= 'Z'
    
    def _is_digit(self, char: str) -> bool:
        return '0' <= char <= '9'
    
OK = NameValidator.Result(None)
NO_VALIDATOR = NoNameValidator()
UTF_VALIDATOR = UtfNameValidator()
STRICT_VALIDATION = StrictNameValidator()