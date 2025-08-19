from typing import Optional, Dict, Any

import logging
from requests import get, post
from requests.exceptions import RequestException
import sys

from mcp.server.fastmcp import FastMCP

from common import Response, Configure

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class Default:
    kali_server = f"http://localhost:{Configure.port.kali}"
    perplexity_server = f"http://localhost:{Configure.port.perplexity}"

def resolve(data): return Response(True, data, None)
def reject(why): return Response(False, None, why)

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

mcp = FastMCP("Kali + SBOM")

def setup_perplexity(server: str, timeout: int):
    if not Configure.use_perplexity:
        return
    
    client = Client(server, timeout)
    
    @mcp.tool()
    def perplexity_search(query: str):
        return client.post("/api/search", { "query": query })

def setup_kali(server: str, timeout: int):
    client = Client(server, timeout)
    run = lambda tool, **kwargs: client.post(f"/api/tools/{tool}", kwargs)
    
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
    setup_kali(Default.kali_server, Configure.timeout)
    setup_perplexity(Default.perplexity_server, Configure.timeout)
    mcp.run(transport="stdio")
