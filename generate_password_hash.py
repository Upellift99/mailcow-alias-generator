#!/usr/bin/env python3
"""
Generate a secure password hash for use in config.json.

Usage:
    python generate_password_hash.py                # prompts for the password
    python generate_password_hash.py "mypassword"   # password as argument

Copy the printed value into the "password" field of a user in config.json.
The application accepts these hashes directly and verifies them securely;
plaintext passwords still work but are discouraged.
"""

import sys
from getpass import getpass

from werkzeug.security import generate_password_hash


def main():
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = getpass("Password to hash: ")
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("❌ Passwords do not match.", file=sys.stderr)
            return 1

    if not password:
        print("❌ Password must not be empty.", file=sys.stderr)
        return 1

    # pbkdf2:sha256 is a sensible, dependency-free default shipped with Werkzeug.
    print(generate_password_hash(password, method="pbkdf2:sha256"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
