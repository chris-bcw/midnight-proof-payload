# Encrypted Prove Client

This client sends encrypted `/prove` requests to the coordinator at `http://172.16.0.37:8080`.

## Setup

1. Paste the proof-server public key hex into `SERVER_PUBLIC_KEY_HEX` in `test_prove.py`.
2. From this directory, run:

```bash
uv run python test_prove.py
```

The client always uses `../preprod-server-7.0.0/prove-a-payload.bin`.

Outputs are written to `./out/`:

- `encrypted-request.bin`
- `encrypted-response.bin`
- `decrypted-response.bin`
- `client-public-key.txt`
- `request-nonce.txt`
- `response-nonce.txt`
