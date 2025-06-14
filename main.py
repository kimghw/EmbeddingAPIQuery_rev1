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
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', type=int, default=8001, help='Port to run the server on')
        args, unknown = parser.parse_known_args()
        uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
