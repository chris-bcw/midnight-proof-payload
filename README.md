Preprod Server Payload Scripts
=============================

Overview
--------
This directory contains three small helper scripts that post binary payload files to a preprod server and save the server responses into an `out/` directory.

Scripts
-------

- `check.sh` - Sends `check-payload.bin` to the server's `/check` endpoint and saves the response to `out/check-response.bin`.
- `prove-a.sh` - Sends `prove-a-payload.bin` to the server's `/prove` endpoint and saves the response to `out/prove-a-response.bin`.
- `prove-b.sh` - Sends `prove-b-payload.bin` to the server's `/prove` endpoint and saves the response to `out/prove-b-response.bin`.

Behavior
--------

- Each script ensures the `out/` directory exists (`mkdir -p out`).
- They accept an optional URL argument; if omitted they default to `http://127.0.0.1:6300`.
- They use `curl -X POST` with `--data-binary` to stream the payload file, saving the HTTP response to a file under `out/`.
- After saving, each script prints the path to the saved response and shows a short `hexdump -C` of the response (first 20 lines are truncated by `head -20`).

Required tools
--------------

- `curl`
- `hexdump` (usually provided by `bsdmainutils` or `hexdump` from `util-linux`)
- A network route from the machine running the scripts to the server URL you provide.

Usage examples
--------------

Run with default URL:

```
./check.sh
./prove-a.sh
./prove-b.sh
```

Run against a custom server URL:

```
./check.sh http://server.example:6300
./prove-a.sh http://server.example:6300
./prove-b.sh http://server.example:6300
```

Notes
-----

- Each script expects its corresponding payload file to be present in the same directory:
  - `check-payload.bin`
  - `prove-a-payload.bin`
  - `prove-b-payload.bin`
- Responses are written to `out/` as the scripts show when they complete.

Files
-----

- See [preprod-server-7.0.0/check.sh](preprod-server-7.0.0/check.sh)
- See [preprod-server-7.0.0/prove-a.sh](preprod-server-7.0.0/prove-a.sh)
- See [preprod-server-7.0.0/prove-b.sh](preprod-server-7.0.0/prove-b.sh)
