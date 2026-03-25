# pdd-express

[English](./README.md) | [中文](./README.zh-CN.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Version](https://img.shields.io/badge/version-1.0-brightgreen)
![SQLite](https://img.shields.io/badge/database-SQLite-07405E)
![OpenClaw](https://img.shields.io/badge/Acknowledgement-OpenClaw-6f42c1)

A lightweight Flask-based service for managing user phone bindings and querying package information for PDD express workflows.

## Features

- User phone number management
  - List phone numbers by `wxid`
  - Add / update / delete phone numbers
- Package query API
- WeChat login endpoint
- SQLite-backed local storage
- `.env`-based configuration
- Standard Python `logging` with rotating log files
- Database initialization and migration scripts

## Quick Start

### 1. Clone the project

```bash
git clone git@github.com:Einck0/pdd-express.git
cd pdd-express
```

### 2. Create environment file

```bash
cp .env.example .env
```

## Local Development

### 1. Create Python environment and install dependencies

Using `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Or using built-in `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize database

```bash
python3 src/init_db.py
```

### 3. Run locally

```bash
python3 src/main.py
```

Default local port:
- `5000`

## Docker Usage

### Start with Docker Compose

```bash
docker compose up --build
```

Docker port mapping:
- host `15000` -> container `5000`

## Project Structure

```text
pdd-express/
├── src/
│   ├── main.py               # Flask app entrypoint
│   ├── settings.py           # Configuration loading (.env / env vars)
│   ├── logging_config.py     # Logging setup
│   ├── database.py           # Database connection management
│   ├── repository.py         # Data access layer
│   ├── user_service.py       # Business logic for user phone management
│   ├── PackageService.py     # Package query service
│   ├── res.js                # JS resource used for anti-content generation
│   ├── init_db.py            # Initialize database schema
│   └── migrate_phones.py     # Migrate old phone data into new schema
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── README.md
├── README.zh-CN.md
├── VERSIONED_NOTES.md
└── CLEANUP_NOTES.md
```

## Requirements

- Python 3.10+ recommended
- Node.js available for `pyexecjs` / `src/res.js` execution
- SQLite

## Configuration

This project uses **`.env`** as the primary configuration source.

Example variables:

```env
PDD_APP_HOST=0.0.0.0
PDD_APP_PORT=5000
PDD_APP_DEBUG=false
PDD_API_PREFIX=/express
PDD_WECHAT_APPID=
PDD_WECHAT_SECRET=
PDD_SQLITE_DATABASE_DIR=./
PDD_SQLITE_DATABASE_NAME=pdd.db
PDD_MOBILE=
PDD_ENCRYPTED_PASSWORD=
PDD_COOKIE_STRING=
PDD_USER_AGENT=Mozilla/5.0 ...
```

## Database Setup

Initialize the database schema:

```bash
python3 src/init_db.py
```

If you have old backup data that needs migration:

```bash
python3 src/migrate_phones.py
```

## API Overview

Base prefix:

```text
/express
```

### Phone APIs
- `GET /express/phones/<wxid>`
- `POST /express/phones/<wxid>`
- `PUT /express/phones/<wxid>`
- `DELETE /express/phones/<wxid>`

### Package APIs
- `POST /express/package/<wxid>`
- `GET /express/package/<wxid>`

### Auth API
- `POST /express/wxlogin`

## Acknowledgements

Special thanks to the **OpenClaw** project for providing the agent environment and workflow support that helped drive part of this refactor and project organization.

- OpenClaw: <https://github.com/openclaw/openclaw>
- Docs: <https://docs.openclaw.ai>

## License

Add a project license here if needed.
