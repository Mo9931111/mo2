#!/usr/bin/env python3
"""Simple helper to preview the spare parts mockup in a browser."""
from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import socket
import socketserver
import sys
import webbrowser
from pathlib import Path

DEFAULT_FILENAME = "spare_parts_mockup.html"
DEFAULT_PORT = 8000


def positive_int(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not (0 < port < 65536):
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def available_port(preferred: int) -> int:
    """Return an available TCP port, falling back to 0 (random) if needed."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
        except OSError:
            sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start a lightweight HTTP server for the spare parts mockup.",
    )
    parser.add_argument(
        "--port",
        type=positive_int,
        default=DEFAULT_PORT,
        help=f"Port to bind to (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open a browser window automatically.",
    )
    parser.add_argument(
        "--filename",
        default=DEFAULT_FILENAME,
        help="Mockup filename to open relative to the design directory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    repo_root = Path(__file__).resolve().parents[1]
    design_dir = repo_root / "design"
    if not design_dir.exists():
        print("Could not find the design directory.", file=sys.stderr)
        return 1

    file_to_open = design_dir / args.filename
    if not file_to_open.exists():
        print(f"Could not find {file_to_open.relative_to(repo_root)}", file=sys.stderr)
        return 1

    port = available_port(args.port)
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(design_dir)
    )

    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/{file_to_open.name}"
        print(f"Serving {file_to_open.relative_to(repo_root)} at {url}")
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping preview server...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
