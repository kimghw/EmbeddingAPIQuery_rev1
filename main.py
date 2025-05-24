"""
Main entry point for Document Embedding & Retrieval System.
"""

import asyncio
from fastapi import FastAPI
from interfaces.api.main import app
from interfaces.cli.main import cli
import sys


def main():
    """Main entry point that can handle both CLI and API modes."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['cli', 'command']:
        # CLI mode
        cli()
    else:
        # API mode (default)
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
