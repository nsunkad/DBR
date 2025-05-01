from pydantic import BaseModel, Field, field_serializer
from typing import Callable, List
from enums import FunctionType
import dill

class Function(BaseModel):
    f: Callable
    function_type: FunctionType
    
    @field_serializer("f")
    def serialize_logic_function(self, f: Callable) -> List[str]:
        f.__module__ = '__main__'
        dump = dill.dumps(f).hex()
        return dump

class TransformFunction(Function):
    f: Callable
    
    def __init__(self, f):
        super().__init__(f=f, function_type=FunctionType.TRANSFORM)

class ExecuteFunction(Function):
    f: Callable

    def __init__(self, f):
        super().__init__(f=f, function_type=FunctionType.EXECUTE)
