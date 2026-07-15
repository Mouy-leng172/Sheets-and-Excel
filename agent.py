#!/usr/bin/env python3
"""
Local file-management agent.
Scope: operates ONLY on the local filesystem. No network or remote-device
functionality. Intended for managing your own trading logs/reports/archives.

Commands:
    read      <file>
    create    <file> --content "text"
    compress  <output.zip> <file1> [file2 ...]
    encrypt   <file> --password "..."
    decrypt   <file.enc> --password "..."

Encryption: PBKDF2-HMAC-SHA256 key derivation + Fernet (AES-128-CBC + HMAC).
Requires: pip install cryptography --break-system-packages
"""
import argparse
import base64
import getpass
import os
import sys
import zipfile

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
KDF_ITERATIONS = 390_000


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def cmd_read(args):
    path = args.file
    if not os.path.isfile(path):
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        print(f.read())


def cmd_create(args):
    path = args.file
    if os.path.exists(path) and not args.force:
        print(f"Error: '{path}' already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(args.content or "")
    print(f"Created '{path}' ({len(args.content or '')} bytes).")


def cmd_compress(args):
    out_path = args.output
    missing = [p for p in args.files if not os.path.isfile(p)]
    if missing:
        print(f"Error: missing file(s): {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in args.files:
            zf.write(p, arcname=os.path.basename(p))
    print(f"Created archive '{out_path}' with {len(args.files)} file(s).")


def cmd_encrypt(args):
    path = args.file
    if not os.path.isfile(path):
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    password = args.password or getpass.getpass("Password: ")
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    with open(path, "rb") as f:
        data = f.read()
    token = fernet.encrypt(data)
    out_path = path + ".enc"
    with open(out_path, "wb") as f:
        f.write(salt + token)
    print(f"Encrypted -> '{out_path}'.")


def cmd_decrypt(args):
    path = args.file
    if not os.path.isfile(path):
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    password = args.password or getpass.getpass("Password: ")
    with open(path, "rb") as f:
        raw = f.read()
    salt, token = raw[:SALT_SIZE], raw[SALT_SIZE:]
    key = derive_key(password, salt)
    fernet = Fernet(key)
    try:
        data = fernet.decrypt(token)
    except Exception:
        print("Error: wrong password or corrupted file.", file=sys.stderr)
        sys.exit(1)
    out_path = path[:-4] if path.endswith(".enc") else path + ".dec"
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"Decrypted -> '{out_path}'.")


def main():
    parser = argparse.ArgumentParser(description="Local file management agent")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("read", help="Read and print a file")
    p.add_argument("file")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("create", help="Create a new text file")
    p.add_argument("file")
    p.add_argument("--content", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("compress", help="Zip one or more files")
    p.add_argument("output")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_compress)

    p = sub.add_parser("encrypt", help="Encrypt a file with a password")
    p.add_argument("file")
    p.add_argument("--password", default=None)
    p.set_defaults(func=cmd_encrypt)

    p = sub.add_parser("decrypt", help="Decrypt a .enc file with a password")
    p.add_argument("file")
    p.add_argument("--password", default=None)
    p.set_defaults(func=cmd_decrypt)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
