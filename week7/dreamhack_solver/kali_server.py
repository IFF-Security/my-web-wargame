from typing import Optional, Any

from dataclasses import dataclass
from functools import wraps
import logging
from os.path import join, exists
from subprocess import Popen, PIPE, TimeoutExpired
import sys
from threading import Thread
import traceback

from flask import Flask, request, jsonify

from common import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


app = Flask(__name__)

class CommandExecutor:
    process: Popen[str]
    def __init__(self, command: str, timeout: int = Configure.timeout):
        self.command = command
        self.timeout = timeout

        self.process = None
        self.stdout = ""
        self.stderr = ""
        self.return_code = None
        self.timed_out = False
    
    def makeResult(self):
        return CommandResult(
            self.stdout,
            self.stderr,
            self.return_code,
            self.return_code != -1 and \
                ((self.stdout or self.stderr) or (self.return_code == 0)),
            self.timed_out,
            self.timed_out and (self.stdout or self.stderr)
        )

    def _read_stdout(self):
        for line in iter(self.process.stdout.readline, ''):
            self.stdout += line
    
    def _read_stderr(self):
        for line in iter(self.process.stderr.readline, ''):
            self.stderr += line
    
    def run_thread(self, func):
        thread = Thread(target=func)
        thread.daemon = True
        thread.start()
        return thread
    
    def execute(self, wrap=True):
        logger.info(f"Executing command: {self.command}")
        try:
            self.process = Popen(
                self.command,
                shell=True, stdout=PIPE, stderr=PIPE, text=True, bufsize=1
            )

            stdout_thread = self.run_thread(self._read_stdout)
            stderr_thread = self.run_thread(self._read_stderr)

            try:
                self.return_code = self.process.wait(timeout=self.timeout)
                stdout_thread.join()
                stderr_thread.join()
            except TimeoutExpired:
                logger.warning("Command timed out, terminating.")
                self.timed_out = True
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except TimeoutExpired:
                    logger.warning("Process not terminated, killing.")
                    self.process.kill()
                self.return_code = -1
        except Exception as e:
            logger.error(f"Error while executing command: {str(e)}")
            logger.error(traceback.format_exc())
            self.stderr = f"Error executing command: {str(e)}\n{self.stderr}"
            self.return_code = -1

        if self.stderr:
            logger.error(f"stderr of {self.command}:\n{self.stderr}")

        if not wrap:
            return self.makeResult()
        
        return jsonify(self.makeResult())

class MissingParameter(Exception):
    def __init__(self, name: str, *args):
        super().__init__(*args)
        self.name = name

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

@app.post("/api/tools/command")
@tool
def generic_command():
    param = get_param(Field('command', required=True))
    return CommandExecutor(param['command']).execute()

@app.post("/api/tools/curl")
@tool
def curl():
    param = get_param(Field("target", required=True),
                      Field("method", default="GET"),
                      Field("data", default=""),
                      Field("content_type", default="text/plain"))
    command = f"{Kali.curl} {param['target']} -X {param['method']}"
    data: str = param['data']
    data = data.replace('"', '\\"')
    command += f" -d {data}"
    if param['content_type'] != "text/plain":
        command += f" -H \"Content-Type: {param['content_type']}\""
    return CommandExecutor(command).execute()

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
    CommandExecutor(command).execute()

    command = f"grep -r 'CVE' /tmp/sbom.json"
    return CommandExecutor(command).execute()

@app.get('/health')
def health():
    essential = ["curl", "trivy"]
    status = {}
    for tool in essential:
        try:
            result = CommandExecutor(f"which {tool}").execute(wrap=False)
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
    app.run(host="0.0.0.0", port=Configure.port.kali)
