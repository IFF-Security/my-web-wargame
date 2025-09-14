from common import CommandResult, Configure
from logger import getLogger


from flask import jsonify


import traceback
from subprocess import PIPE, Popen, TimeoutExpired
from threading import Thread

logger = getLogger(__name__)


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

    def execute(self, wrap):
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

        result = CommandResult(
            self.stdout,
            self.stderr,
            self.return_code,
            self.return_code != -1 and \
                ((self.stdout or self.stderr) or (self.return_code == 0)),
            self.timed_out,
            self.timed_out and (self.stdout or self.stderr)
        )

        if wrap:
            result = jsonify(result)

        return result


def execute(command: str, wrap=True):
    return CommandExecutor(command).execute(wrap)
