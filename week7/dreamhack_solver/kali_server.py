from typing import Optional, Any

from dataclasses import dataclass
from functools import wraps
from os.path import join, exists
import traceback

from flask import Flask, request, jsonify

from common import Configure
from commandExecutor import execute
from logger import getLogger

logger = getLogger(__name__)
app = Flask(__name__)


class MissingParameter(Exception):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name


@dataclass
class Field:
    name: str
    required: bool = False
    default: Optional[Any] = None


def get_param(*fields: Field):
    params = {}
    if request.headers.get('Content-Type') == 'application/json':
        params = dict(request.json)
    rst = {}
    for field in fields:
        data = params.get(field.name, field.default)
        if isinstance(data, str):
            data = data.strip()
        if data == None:
            if not field.required:
                continue
            else:
                raise MissingParameter(field.name)
        rst[field.name] = data
    return rst


def tool(func):
    @wraps(func)
    def deco():
        try:
            return func()
        except MissingParameter as e:
            logger.warning(f"Missing parameter: {e.name}")
            return jsonify({ "error": f"Missing parameter: {e.name}" }), 400
        except Exception as e:
            logger.error(f"Error while executing command: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({ "error": f"Server error: {str(e)}" }), 500
    return deco


@app.post("/api/tools/command")
@tool
def generic_command():
    param = get_param(Field('command', required=True))
    return execute(param['command'])


@app.post("/api/tools/curl")
@tool
def curl():
    param = get_param(Field("target", required=True),
                      Field("method", default="GET"),
                      Field("data", default=""),
                      Field("content_type", default="text/plain"))
    command = f"curl {param['target']} -X {param['method']}"
    data: str = param['data']
    data = data.replace('"', '\\"')
    if data:
        command += f" -d {data}"
    if param['content_type'] != "text/plain":
        command += f" -H \"Content-Type: {param['content_type']}\""
    return execute(command)


@app.post("/api/tools/trivy")
@tool
def trivy():
    param = get_param(Field("file_path", required=True))
    path = param['file_path']

    package_lock = join(path, 'package-lock.json')
    
    if not exists(package_lock):
        return jsonify({
            "error": f"pachage-lock.json not found in: {path}"
        }), 400
    
    command = f"trivy fs --format cyclonedx --scanners vuln --output /tmp/sbom.json \"{package_lock}\""
    execute(command)

    command = f"grep -r 'CVE' /tmp/sbom.json"
    return execute(command)


@app.get('/health')
def health():
    essential = ["curl", "trivy"]
    status = {}
    for tool in essential:
        try:
            result = execute(f"which {tool}", False)
            status[tool] = result["success"]
        except:
            status[tool] = False
    return jsonify({
        "status": "healthy",
        "message": "Kali Linux Tools API Server is running",
        "tools_status": status,
        "all_essential_tools_available": all(status.values())
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Configure.port)
