from __future__ import annotations

import math
from typing import override
from pyavro.logicaltype import LogicalType
from pyavro.schema import Schema, Type

class LogicalTypes:
    DECIMAL = "decimal"
    BIG_DECIMAL = "big-decimal"
    DURATION = "duration"
    UUID = "uuid"
    DATE = "date"
    TIME_MILLIS = "time-millis"
    TIME_MICROS = "time-micros"
    TIMESTAMP_MILLIS = "timestamp-millis"
    TIMESTAMP_MICROS = "timestamp-micros"
    TIMESTAMP_NANOS = "timestamp-nanos"
    LOCAL_TIMESTAMP_MILLIS = "local-timestamp-millis"
    LOCAL_TIMESTAMP_MICROS = "local-timestamp-micros"
    LOCAL_TIMESTAMP_NANOS = "local-timestamp-nanos"

class Uuid(LogicalType):
    UUID_BYTES = 16

    def __init__(self):
        super().__init__(LogicalTypes.UUID)
    
    @override
    def validate(self, schema):
        super().validate(schema)
        if (schema.type != Type.STRING and schema.type != Type.FIXED):
            raise ValueError("Uuid can only be used with an underlying string or fixed type")
        if (schema.type == Type.FIXED and schema.get_fixed_size() != self.UUID_BYTES):
            raise ValueError(f"Uuid with fixed type must have a size of {self.UUID_BYTES} bytes")

class Duration(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.DURATION)

    @override
    def validate(self, schema):
        super().validate(schema)
        if schema.type != Type.FIXED or schema.get_fixed_size() != 12:
            raise ValueError("Duration can only be used with an underlying fixed type of size 12")

class Decimal(LogicalType):
    PRECISION_PROP = "precision"
    SCALE_PROP = "scale"

    def __init__(self, precision: int, scale: int):
        super().__init__(LogicalTypes.DECIMAL)
        self.precision = precision
        self.scale = scale

    @classmethod
    def create_from_schema(cls, schema: Schema) -> Decimal:
        def get_int(name):
            prop = schema.get_object_prop(name)
            if not isinstance(prop, int):
                raise ValueError(f"Expected int {name}: {prop.__class__.__name__}")
            return prop
        if not cls.PRECISION_PROP in schema:
            raise ValueError("Invalid decimal: missing precision")
        precision = get_int(cls.PRECISION_PROP)
        scale = 0
        if cls.SCALE_PROP in schema:
            scale = get_int(cls.SCALE_PROP)
        return cls(precision=precision, scale=scale)
    
    @override
    def add_to_schema(self, schema: Schema) -> Schema:
        super().add_to_schema(schema)
        schema.add_prop(self.PRECISION_PROP, self.precision)
        schema.add_prop(self.SCALE_PROP, self.scale)
        return schema
    # TODO: continue here

    @override
    def validate(self, schema):
        super().validate(schema)
        if schema.type != Type.FIXED and schema.type != Type.BYTES:
            raise ValueError("Logical type decimal must be backed by fixed or bytes")
        if self.precision < 0:
            raise ValueError(f"Invalid decimal precision: {self.precision} (must be positive)")
        elif self.precision > self.max_precision(schema):
            if schema.type == Type.FIXED:
                raise ValueError(f'fixed({schema.get_fixed_size()}) cannot store {self.precision} digits (max {self.max_precision(schema)})')
            else:
                raise ValueError(f'Invalid precision for decimal backed by bytes: {self.precision} (max {self.max_precision(schema)})')
        if self.scale < 0:
            raise ValueError(f"Invalid decimal scale: {self.scale} (must be positive)")
        elif self.scale > self.precision:
            raise ValueError(f"Invalid decimal scale: {self.scale} (greater than precision: {self.precision})")
        
    def max_precision(self, schema: Schema) -> int:
        if schema.type == Type.BYTES:
            return 2147483647
        if schema.type == Type.FIXED:
            size: int = schema.get_fixed_size()
            return round(math.floor(math.log10(2) * (8 * size - 1)))
        return 0
    
    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, LogicalTypes.Decimal):
            return self.precision == other.precision and self.scale == other.scale
        return False
    
    def __hash__(self):
        return 31 * self.precision + self.scale
    
class BigDecimal(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.BIG_DECIMAL)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.BYTES:
            raise ValueError("BigDecimal can only be used with an underlying bytes type")
        
class Date(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.DATE)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.INT:
            raise ValueError("Date can only be used with an underlying int type")

class TimeMillis(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.TIME_MILLIS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.INT:
            raise ValueError("Time (millis) can only be used with an underlying int type")

class TimeMicros(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.TIME_MICROS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Time (micros) can only be used with an underlying long type")

class TimestampMillis(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.TIMESTAMP_MILLIS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Timestamp (millis) can only be used with an underlying long type")

class TimestampMicros(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.TIMESTAMP_MICROS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Timestamp (micros) can only be used with an underlying long type")

class TimestampNanos(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.TIMESTAMP_NANOS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Timestamp (nanos) can only be used with an underlying long type")

class LocalTimestampMillis(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.LOCAL_TIMESTAMP_MILLIS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Local timestamp (millis) can only be used with an underlying long type")

class LocalTimestampMicros(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.LOCAL_TIMESTAMP_MICROS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Local timestamp (micros) can only be used with an underlying long type")

class LocalTimestampNanos(LogicalType):
    def __init__(self):
        super().__init__(LogicalTypes.LOCAL_TIMESTAMP_NANOS)
    
    @override
    def validate(self, schema: Schema):
        super().validate(schema)
        if schema.type != Type.LONG:
            raise ValueError("Local timestamp (nanos) can only be used with an underlying long type")

def from_schema(schema: Schema, ignore_invalid: bool = False):
    logical_type: LogicalType
    type_name: str = schema.get_object_prop(LogicalType.LOGICAL_TYPE_PROP)

    if type_name is None:
        return None
    try:
        match type_name:
            case LogicalTypes.DECIMAL:
                logical_type = Decimal.create_from_schema(schema)
            case LogicalTypes.BIG_DECIMAL:
                logical_type = BIG_DECIMAL_TYPE
            case LogicalTypes.DURATION:
                logical_type = DURATION_TYPE
            case LogicalTypes.UUID:
                logical_type = UUID_TYPE
            case LogicalTypes.DATE:
                logical_type = DATE_TYPE
            case LogicalTypes.TIME_MILLIS:
                logical_type = TIME_MILLIS_TYPE
            case LogicalTypes.TIME_MICROS:
                logical_type = TIME_MICROS_TYPE
            case LogicalTypes.TIMESTAMP_MILLIS:
                logical_type = TIMESTAMP_MILLIS_TYPE
            case LogicalTypes.TIMESTAMP_MICROS:
                logical_type = TIMESTAMP_MICROS_TYPE
            case LogicalTypes.TIMESTAMP_NANOS:
                logical_type = TIMESTAMP_NANOS_TYPE
            case LogicalTypes.LOCAL_TIMESTAMP_MILLIS:
                logical_type = LOCAL_TIMESTAMP_MILLIS_TYPE
            case LogicalTypes.LOCAL_TIMESTAMP_MICROS:
                logical_type = LOCAL_TIMESTAMP_MICROS_TYPE
            case LogicalTypes.LOCAL_TIMESTAMP_NANOS:
                logical_type = LOCAL_TIMESTAMP_NANOS_TYPE
            case _:
                logical_type = None
            
        if logical_type is not None:
            logical_type.validate(schema)
    except Exception as e:
        print(f"Invalid logical type found: {e}")
        if not ignore_invalid:
            raise e
        print(f"Ignoring invalid logical type for name: {type_name}")
        return None
    
    return logical_type

BIG_DECIMAL_TYPE = BigDecimal()
UUID_TYPE = Uuid()
DURATION_TYPE = Duration()
DATE_TYPE = Date()
TIME_MILLIS_TYPE = TimeMillis()
TIME_MICROS_TYPE = TimeMicros()
TIMESTAMP_MILLIS_TYPE = TimestampMillis()
TIMESTAMP_MICROS_TYPE = TimestampMicros()
TIMESTAMP_NANOS_TYPE = TimestampNanos()
LOCAL_TIMESTAMP_MILLIS_TYPE = LocalTimestampMillis()
LOCAL_TIMESTAMP_MICROS_TYPE = LocalTimestampMicros()
LOCAL_TIMESTAMP_NANOS_TYPE = LocalTimestampNanos()
def decimal(precision: int, scale: int = 0) -> Decimal:
    return Decimal(precision, scale)