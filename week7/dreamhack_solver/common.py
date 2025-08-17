from typing import Any, Dict, Optional
from dataclasses import dataclass

class Configure:
    class port:
        kali = 5000
        perplexity = 5050
    use_perplexity = False # TODO: Update this to True after get perplexity api
    timeout = 3 * 60

class Kali:
    curl = "curl"
    trivy = "trivy"
    command = "command"

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
