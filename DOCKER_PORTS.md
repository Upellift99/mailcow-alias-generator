# Docker Port Configuration

## Problem Solved

Ports were previously hardcoded (5000) in multiple Docker configuration files. This configuration has been made flexible to allow easy customization.

## Current Configuration

### Available Environment Variables

- `HOST_PORT`: Port on the host (default: 5000) - **This is what you change to expose on different ports**

### Modified Files

1. **docker-compose.yml**: Now uses `${HOST_PORT:-5000}:5000` (container always uses 5000)
2. **Dockerfile**: Uses `ENV PORT=5000` and `EXPOSE $PORT`
3. **.env**: New file to define default values

## Usage

### Method 1: Modify the .env file

```bash
# Edit the .env file to change external port
HOST_PORT=50539
```

### Method 2: Environment variables at launch

```bash
# Launch with custom external port
HOST_PORT=50539 docker compose up -d

# Or export variables
export HOST_PORT=50539
docker compose up -d
```

### Method 3: Override in docker-compose

```yaml
# Create a docker-compose.override.yml
services:
  mailcow-alias-generator:
    ports:
      - "50539:5000"  # External:Internal
```

## Usage Examples

### Standard port (5000)
```bash
docker compose up -d
# Accessible at http://localhost:5000
```

### Custom port (50539)
```bash
HOST_PORT=50539 docker compose up -d
# Accessible at http://localhost:50539
```

### Multiple instances
```bash
# Instance 1
HOST_PORT=5001 docker compose -p alias-gen-1 up -d

# Instance 2
HOST_PORT=5002 docker compose -p alias-gen-2 up -d
```

## Troubleshooting

### Port not accessible after changing HOST_PORT

1. **Stop the container**: `docker compose down`
2. **Verify your .env file**: Make sure `HOST_PORT=50539` (or your desired port)
3. **Restart**: `docker compose up -d`
4. **Check the mapping**: `docker compose ps` should show `0.0.0.0:50539->5000/tcp`
5. **Test**: `curl http://localhost:50539/api/status`

## Important Notes

- The `docker-start.sh` script automatically reads the port from `config.json`
- Health checks automatically adapt to the configured port
- The `.env` file can be versioned or ignored as needed (see `.gitignore`)