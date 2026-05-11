#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime, UTC
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_URL = "http://172.16.0.37:8080"
DEFAULT_PAYLOAD = SCRIPT_DIR / "prove-a-payload.bin"
DEFAULT_OUTPUT = SCRIPT_DIR / "out/prove-a-response.bin"


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send prove-a payload, print proof-job-id immediately, then save the response body."
    )
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="Proof server base URL")
    parser.add_argument(
        "--payload",
        type=Path,
        default=DEFAULT_PAYLOAD,
        help="Payload file to send",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="File to write the response body to",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    output_path = args.output.resolve()
    base_url = args.url.rstrip("/")
    request_url = f"{base_url}/prove"
    payload = payload_path.read_bytes()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"payload={payload_path} bytes={len(payload)}")
    print(f"url={request_url}")

    request = urllib.request.Request(request_url, data=payload, method="POST")
    request.add_header("Content-Type", "application/octet-stream")

    try:
        with urllib.request.urlopen(request) as response:
            print(f"status={response.status}")
            print(f"headers-received-at={now_iso()}")
            print(f"proof-job-id={response.headers.get('proof-job-id', '<missing>')}")
            response_nonce = response.headers.get("response-nonce")
            if response_nonce is not None:
                print(f"response-nonce={response_nonce}")

            body = response.read()
            print(f"body-received-at={now_iso()}")
    except urllib.error.HTTPError as err:
        print(f"status={err.code}", file=sys.stderr)
        print(
            f"proof-job-id={err.headers.get('proof-job-id', '<missing>')}",
            file=sys.stderr,
        )
        error_body = err.read()
        if error_body:
            print(error_body.decode("utf-8", errors="replace"), file=sys.stderr)
        return 1
    except urllib.error.URLError as err:
        print(f"connection-error={err.reason}", file=sys.stderr)
        parsed = urllib.parse.urlparse(request_url)
        print(f"host={parsed.hostname} port={parsed.port}", file=sys.stderr)
        return 2

    output_path.write_bytes(body)
    print(f"response-saved={output_path}")
    print(f"response-bytes={len(body)}")
    print(f"first-32-bytes={body[:32].hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
