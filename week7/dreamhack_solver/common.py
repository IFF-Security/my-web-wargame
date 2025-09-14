from typing import Any, Dict, Optional
from dataclasses import dataclass

class Configure:
    port = 5000
    timeout = 3 * 60

@dataclass
class CommandResult:
    stdout: str
    stderr: str
    return_code: int
    success: bool
    timed_out: bool
    partial_results: bool

@dataclass
class Response:
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]

def resolve(data): return Response(True, data, None)
def reject(why): return Response(False, None, why)
