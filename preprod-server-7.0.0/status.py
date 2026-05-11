#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import urllib.parse
import urllib.error
import urllib.request
from datetime import UTC, datetime


DEFAULT_URL = "http://172.16.0.37:8080"


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch proof job status with a single /status lookup."
    )
    parser.add_argument("job_id", help="Proof job UUID")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="Proof server base URL")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = args.url.rstrip("/")
    query = urllib.parse.urlencode({"jobId": args.job_id})
    request_url = f"{base_url}/status?{query}"

    print(f"url={request_url}")
    print(f"requested-at={now_iso()}")

    request = urllib.request.Request(request_url, method="GET")

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read()
            print(f"status={response.status}")
            print(f"response-received-at={now_iso()}")
    except urllib.error.HTTPError as err:
        print(f"status={err.code}", file=sys.stderr)
        print(f"response-received-at={now_iso()}", file=sys.stderr)
        error_body = err.read()
        if error_body:
            print(f"body={error_body.decode('utf-8', errors='replace')}", file=sys.stderr)
        return 1
    except urllib.error.URLError as err:
        print(f"connection-error={err.reason}", file=sys.stderr)
        parsed = urllib.parse.urlparse(request_url)
        print(f"host={parsed.hostname} port={parsed.port}", file=sys.stderr)
        return 2

    print(f"body={body.decode('utf-8', errors='replace')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
