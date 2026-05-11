from __future__ import annotations

import secrets
import sys
import urllib.error
import urllib.request
from pathlib import Path

from nacl.public import Box, PrivateKey, PublicKey


DEFAULT_URL = "http://172.16.0.37:8080"
DEFAULT_PAYLOAD = Path("../preprod-server-7.0.0/prove-a-payload.bin")
DEFAULT_OUT_DIR = Path("out")
SERVER_PUBLIC_KEY_HEX = "9a0e4c505af2d973a53339b027d392259718eeaad6137235c66da9da116c652a"


def post_bytes(
    url: str, body: bytes, headers: dict[str, str] | None = None
) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/octet-stream")
    for name, value in (headers or {}).items():
        req.add_header(name, value)

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, dict(resp.headers.items()), resp.read()
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers.items()), err.read()


def load_server_public_key() -> PublicKey:
    return PublicKey(bytes.fromhex(SERVER_PUBLIC_KEY_HEX))


def write_output(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def print_result(label: str, status: int, headers: dict[str, str], body: bytes) -> None:
    print(f"[{label}] status={status} bytes={len(body)}")
    if "proof-job-id" in headers:
        print(f"[{label}] proof-job-id={headers['proof-job-id']}")
    if "response-nonce" in headers:
        print(f"[{label}] response-nonce={headers['response-nonce']}")
    print(f"[{label}] first-32-bytes={body[:32].hex()}")


def run_encrypted(base_url: str, payload: bytes, out_dir: Path) -> int:
    server_public_key = load_server_public_key()
    client_private_key = PrivateKey.generate()
    client_public_key_hex = bytes(client_private_key.public_key).hex()
    request_nonce = secrets.token_bytes(Box.NONCE_SIZE)
    request_nonce_hex = request_nonce.hex()

    box = Box(client_private_key, server_public_key)
    encrypted_request = box.encrypt(payload, request_nonce)
    ciphertext = encrypted_request.ciphertext

    write_output(out_dir / "encrypted-request.bin", ciphertext)
    write_output(
        out_dir / "client-public-key.txt", f"{client_public_key_hex}\n".encode()
    )
    write_output(out_dir / "request-nonce.txt", f"{request_nonce_hex}\n".encode())
    status, headers, encrypted_response = post_bytes(
        f"{base_url}/prove",
        ciphertext,
        headers={
            "client-public-key": client_public_key_hex,
            "request-nonce": request_nonce_hex,
        },
    )
    write_output(out_dir / "encrypted-response.bin", encrypted_response)
    print_result("encrypted", status, headers, encrypted_response)

    if status != 200:
        return status

    response_nonce_hex = headers.get("response-nonce")
    if response_nonce_hex is None:
        raise ValueError("Encrypted response did not include response-nonce header")

    write_output(out_dir / "response-nonce.txt", f"{response_nonce_hex}\n".encode())
    decrypted_response = box.decrypt(
        encrypted_response, bytes.fromhex(response_nonce_hex)
    )
    write_output(out_dir / "decrypted-response.bin", decrypted_response)
    print(
        f"[encrypted] decrypted-bytes={len(decrypted_response)} first-32-bytes={decrypted_response[:32].hex()}"
    )
    return status


def main() -> int:
    payload_path = DEFAULT_PAYLOAD.resolve()
    out_dir = DEFAULT_OUT_DIR.resolve()
    payload = payload_path.read_bytes()

    print(f"payload={payload_path} bytes={len(payload)}")
    print(f"url={DEFAULT_URL}/prove")

    try:
        status = run_encrypted(DEFAULT_URL.rstrip("/"), payload, out_dir)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 2

    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
