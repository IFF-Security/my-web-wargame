from typing import Optional, Dict, Any

from requests import get, post
from requests.exceptions import RequestException

from mcp.server.fastmcp import FastMCP

from common import Configure, resolve, reject
from logger import getLogger

logger = getLogger(__name__)

class Client:
    def __init__(self, server_url: str, timeout: int):
        logger.info(f"Client created with url: {server_url}")
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        try:
            if not params:
                params = {}

            url = self.server_url + endpoint
            resp = get(url, params=params, timeout=self.timeout)
            return resolve(resp.json())
        except RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return reject(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return reject(f"Unexpected error: {str(e)}")
    
    def post(self, endpoint: str, data: Dict[str, Any]):
        url = self.server_url + endpoint
        try:
            resp = post(url, json=data, timeout=self.timeout)
            resp.raise_for_status()
            return resolve(resp.json())
        except RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return reject(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return reject(f"Unexpected error: {str(e)}")
    
    def check_health(self):
        return self.get("/health")

mcp = FastMCP("dreamhack_solver")
client = Client(f"http://localhost:{Configure.port}", Configure.timeout)


def run(tool: str, **kwargs):
    return client.post(f"/api/tools/{tool}", kwargs)

@mcp.tool()
def curl(
    target_url: str,
    method: str = "GET",
    data: str = "",
    content_type: str = "text/plain"
):
    """
    Send HTTP request to target url with given method & data.

    Args:
        target: target url
        method: HTTP Method (GET / POST ; default: GET)
        data: POST body data
        content_type: Content-Type of POST body data (default: text/plain)

    Returns:
        HTTP Request result
    """
    return run("curl", target=target_url, method=method, data=data, content_type=content_type)

@mcp.tool()
def trivy(path: str):
    """
    Get CVE list of given project

    Args:
        path: absolute path of target project
    
    Returns:
        CVE list of given project
    """
    return run("trivy", file_path=path)

@mcp.tool()
def execute_command(command: str):
    """
    Execute an arbitrary command on the Kali linux server.

    Args:
        command: The command to execute
    
    Returns:
        Command execution result
    """
    return run("command", command=command)

if __name__ == "__main__":
    mcp.run(transport="stdio")
