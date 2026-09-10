"""Identical entry point for local development and Render Docker."""
import os
from pathlib import Path
import uvicorn

def port_from_env():
    try:
        port = int(os.environ.get("PORT", "10000"))
    except ValueError as error:
        raise ValueError("PORT must be an integer") from error
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    return port

if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port_from_env(), workers=1,
                proxy_headers=False, access_log=False, server_header=False)
