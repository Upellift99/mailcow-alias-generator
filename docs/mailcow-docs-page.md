<!--
DRAFT for submission to the mailcow documentation ("Third-party apps" section).
This file is NOT part of the application and is not shipped in the Docker image.

How to submit:
  1. Open an existing third-party page on https://docs.mailcow.email/ (e.g. Roundcube)
     and click the "Edit on GitHub" pencil — it lands on the exact file/repo/branch
     that currently powers the docs (their structure was being reorganized at the
     time of writing, so this pencil is the authoritative location).
  2. Add a sibling page using the snippet below, and register it in the nav if needed.
  3. Move the screenshot into their images folder, or keep the absolute raw URL used here.
-->

# Mailcow Alias Generator

[Mailcow Alias Generator](https://github.com/Upellift99/mailcow-alias-generator) is a small,
self-hosted web app that creates email aliases through the mailcow API. It lets you give every
service its own throwaway alias (e.g. `supabase1234@example.com`) that redirects to your real
inbox — useful to compartmentalize signups and spot which service leaked your address.

![Mailcow Alias Generator](https://raw.githubusercontent.com/Upellift99/mailcow-alias-generator/main/screenshots/alias-generator.png){ width="320" }

## Features

- One-click alias creation with a random suffix, live preview and QR code
- Multiple domains, selectable from a dropdown
- Multi-user (per-user password and default redirect address)
- Hashed passwords, login rate limiting, and an optional privacy-friendly [ALTCHA](https://altcha.org/) captcha
- Published Docker image + Docker Compose deployment

## Requirements

- A reachable mailcow instance with the API enabled
- A mailcow API key with **read/write** on `alias` (and read on `domains`)
- Docker + Docker Compose on the host that will run the app

!!! warning "Keep the API key safe"
    The app stores your mailcow API key in its `config.json`. Mount that file read-only,
    restrict access to the app (reverse proxy + HTTPS, firewall/VPN), and use hashed passwords.

## Installation

A pre-built image is published to the GitHub Container Registry, so there is **no need to clone
the repository** — only a `docker-compose.yml` and a `config.json` are required:

```bash
mkdir mailcow-alias-generator && cd mailcow-alias-generator

# Grab the compose file and a config template
curl -O https://raw.githubusercontent.com/Upellift99/mailcow-alias-generator/main/docker-compose.yml
curl -o config.json https://raw.githubusercontent.com/Upellift99/mailcow-alias-generator/main/config.sample.json

# Edit config.json: mailcow_url, api_key, domains and users
docker compose up -d
```

The interface is then available on the configured port (default `5000`, set via `HOST_PORT`).

## Configuration

Minimal `config.json`:

```json
{
  "mailcow_url": "https://mail.example.com",
  "api_key": "YOUR_MAILCOW_API_KEY",
  "domains": ["example.com"],
  "users": {
    "admin": {
      "password": "pbkdf2:sha256:...",
      "default_redirect": "admin@example.com",
      "description": "Administrator"
    }
  }
}
```

!!! tip
    Generate hashed passwords with `python generate_password_hash.py`. Full configuration,
    multi-user setup and ALTCHA options are documented in the project's
    [README](https://github.com/Upellift99/mailcow-alias-generator#readme).

## Links

- Source code: <https://github.com/Upellift99/mailcow-alias-generator>
- Container image: `ghcr.io/upellift99/mailcow-alias-generator:latest`

!!! note
    This is a community-maintained, third-party project and is not affiliated with the mailcow team.
