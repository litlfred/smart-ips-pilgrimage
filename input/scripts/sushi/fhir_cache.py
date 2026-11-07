#!/usr/bin/env python3
"""Lay the FHIR packages pinned in fhir-packages.lock.json into ~/.fhir/packages.

Each tarball is checked against its pinned sha512 integrity before it is
unpacked, so SUSHI loads only pinned packages and downloads nothing.
Standard library only. Run: python3 -I input/scripts/sushi/fhir_cache.py
"""
import base64
import hashlib
import io
import json
import pathlib
import sys
import tarfile
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path.home() / ".fhir" / "packages"


def main():
    lock = json.loads((HERE / "fhir-packages.lock.json").read_text())
    for p in lock["packages"]:
        dest = CACHE / f"{p['name']}#{p['version']}"
        if (dest / "package" / "package.json").exists():
            print(f"fhir-cache: {dest.name} present")
            continue
        algo, want = p["integrity"].split("-", 1)
        data = urllib.request.urlopen(p["tarball"]).read()
        got = base64.b64encode(hashlib.new(algo, data).digest()).decode()
        if got != want:
            print(f"fhir-cache: {p['name']}@{p['version']}: integrity mismatch", file=sys.stderr)
            return 1
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(dest, filter="data")
        print(f"fhir-cache: {dest.name} laid down")
    return 0


if __name__ == "__main__":
    sys.exit(main())
