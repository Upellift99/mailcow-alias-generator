# Docker Port Configuration

## Problem Solved

Ports were previously hardcoded (5000) in multiple Docker configuration files. This configuration has been made flexible to allow easy customization.

## Current Configuration

### Available Environment Variables

- `HOST_PORT`: Port on the host (default: 5000)
- `CONTAINER_PORT`: Port inside the container (default: 5000)

### Modified Files

1. **docker-compose.yml**: Now uses `${HOST_PORT:-5000}:${CONTAINER_PORT:-5000}`
2. **Dockerfile**: Uses `ENV PORT=5000` and `EXPOSE $PORT`
3. **.env**: New file to define default values

## Usage

### Method 1: Modify the .env file

```bash
# Edit the .env file
HOST_PORT=8080
CONTAINER_PORT=5000
```

### Method 2: Environment variables at launch

```bash
# Launch with custom port
HOST_PORT=8080 docker-compose up -d

# Or export variables
export HOST_PORT=8080
export CONTAINER_PORT=5000
docker-compose up -d
```

### Method 3: Override in docker-compose

```yaml
# Create a docker-compose.override.yml
services:
  mailcow-alias-generator:
    ports:
      - "8080:5000"
    environment:
      - PORT=5000
```

## Usage Examples

### Standard port (5000)
```bash
docker-compose up -d
# Accessible at http://localhost:5000
```

### Custom port (8080)
```bash
HOST_PORT=8080 docker-compose up -d
# Accessible at http://localhost:8080
```

### Multiple instances
```bash
# Instance 1
HOST_PORT=5001 docker-compose -p alias-gen-1 up -d

# Instance 2
HOST_PORT=5002 docker-compose -p alias-gen-2 up -d
```

## Important Notes

- The `docker-start.sh` script automatically reads the port from `config.json`
- Health checks automatically adapt to the configured port
- The `.env` file can be versioned or ignored as needed (see `.gitignore`)