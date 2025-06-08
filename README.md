# 🔗 Mailcow Alias Generator

A simple web tool to automate email alias creation via the Mailcow API. Perfect for quickly creating dedicated aliases for each service (e.g., `supabase1234@patopesto.com`).

## ✨ Features

- **Modern web interface**: Bootstrap 5-powered responsive design
- **Intuitive user experience**: Simple and elegant page for creating aliases
- **Automatic generation**: Automatically adds a random 4-digit number
- **Mailcow API integration**: Direct creation via Mailcow API
- **Validation**: Format verification and alias existence checking
- **Logs**: History of created aliases
- **Flexible configuration**: Customizable parameters including port

## 🚀 Installation

### Prerequisites

- Python 3.7+ OR Docker
- Access to a Mailcow instance with API enabled
- Mailcow API key with write permissions

### Option 1: Docker Installation (Recommended)

Docker greatly simplifies installation and deployment. No Python installation required.

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mailcow-alias-generator
   ```

2. **Create configuration file**:
   ```bash
   cp config.sample.json config.json
   ```

3. **Edit the `config.json` file** with your settings:
   ```json
   {
     "mailcow_url": "https://your-mailcow.example.com",
     "api_key": "YOUR_MAILCOW_API_KEY",
     "domain": "example.com",
     "default_redirect": "user@example.com",
     "port": 5000
   }
   ```

4. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **Check status**:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

6. **Access the application** at `http://localhost:5000`

> 💡 **Tip**: Check the [🐳 Docker Usage](#-docker-usage) section for advanced commands and production configuration.

### Option 2: Manual Installation

#### Prerequisites
- Python 3.7+

#### Installation Steps

1. **Clone or download the files** into the `mailcow-alias-generator/` folder

2. **Install Python dependencies**:
   ```bash
   cd mailcow-alias-generator
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   ```bash
   cp config.sample.json config.json
   ```

4. **Edit the `config.json` file** with your settings:
   ```json
   {
     "mailcow_url": "https://your-mailcow.example.com",
     "api_key": "YOUR_MAILCOW_API_KEY",
     "domain": "example.com",
     "default_redirect": "user@example.com",
     "port": 5000
   }
   ```

## 🔧 Mailcow Configuration

### Getting an API Key

1. Log in to your Mailcow interface
2. Go to **Configuration** → **API Access**
3. Create a new API key with permissions:
   - `alias` (read/write)
4. Copy the key into your `config.json`

### Required Permissions

The API key must have at least the following permissions:
- **Alias**: Read and write
- **Domains**: Read (for validation)

## 🎯 Usage

### Starting the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000` (or the port specified in your configuration)

### Web Interface

1. **Open your browser** to `http://localhost:5000` (or your configured port)
2. **Enter the service name** (e.g., `supabase`, `github`, `netflix`)
3. **Check the redirect address** (default: `user@example.com`)
4. **Click "Create Alias"**

The alias will be automatically created with a format like: `supabase1234@example.com`

### REST API

You can also use the API directly (replace 5000 with your configured port):

```bash
curl -X POST http://localhost:5000/api/create-alias \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "github5678@example.com",
    "redirectTo": "user@example.com"
  }'
```

### Check Status

```bash
curl http://localhost:5000/api/status
```

## 📁 File Structure

```
mailcow-alias-generator/
├── app.py                 # Main Flask server
├── index.html             # Web interface (Bootstrap 5)
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── .dockerignore          # Docker ignore file
├── config.json            # Configuration (to be created)
├── config.sample.json     # Configuration example
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── logs/                  # Log directory (Docker volume)
│   ├── mailcow_alias.log  # Application logs
│   └── alias_log.json     # Created aliases history
└── start.sh               # Manual startup script
```

## ⚙️ Configuration Parameters

| Parameter | Description | Example | Required |
|-----------|-------------|---------|----------|
| `mailcow_url` | URL of your Mailcow instance | `https://mail.example.com` | Yes |
| `api_key` | Your Mailcow API key | `YOUR_API_KEY_HERE` | Yes |
| `domain` | Domain for creating aliases | `example.com` | Yes |
| `default_redirect` | Default redirect email address | `user@example.com` | No |
| `port` | Port for the web interface | `5000` | No |

## 🐳 Docker Usage

### Docker Benefits

- **Complete isolation**: Application runs in an isolated environment
- **Simplified deployment**: No need to install Python or dependencies
- **Portability**: Works on any system with Docker
- **Log management**: Persistent volumes for logs
- **Health checks**: Automatic application health monitoring
- **Security**: Runs with non-root user

### Quick Start with Docker Compose (Recommended)

```bash
# 1. Clone and configure
git clone <repository-url>
cd mailcow-alias-generator
cp config.sample.json config.json

# 2. Edit config.json with your settings
nano config.json  # or your preferred editor

# 3. Start the application
docker-compose up -d

# 4. Check status
docker-compose ps
docker-compose logs -f

# 5. Access the application
# http://localhost:5000
```

### Docker Compose Commands

```bash
# Start in background
docker-compose up -d

# View logs in real-time
docker-compose logs -f

# Restart the application
docker-compose restart

# Stop the application
docker-compose down

# Rebuild image (after changes)
docker-compose build --no-cache
docker-compose up -d

# View container status
docker-compose ps

# Access container shell (debug)
docker-compose exec mailcow-alias-generator /bin/bash
```

### Docker Standalone Commands

```bash
# Build the image
docker build -t mailcow-alias-generator .

# Run with custom port
docker run -d \
  --name mailcow-alias-generator \
  -p 8080:5000 \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  mailcow-alias-generator

# Check container status
docker ps
docker logs mailcow-alias-generator

# Stop and remove container
docker stop mailcow-alias-generator
docker rm mailcow-alias-generator
```

### Docker Configuration

#### Environment Variables

The container supports the following environment variables:

```bash
# In docker-compose.yml
environment:
  - PYTHONUNBUFFERED=1  # Unbuffered Python output
  - FLASK_ENV=production  # Production mode
```

#### Volumes

```yaml
volumes:
  - ./config.json:/app/config.json:ro  # Configuration (read-only)
  - ./logs:/app/logs                   # Persistent logs
```

#### Ports

```yaml
ports:
  - "5000:5000"  # Default port
  - "8080:5000"  # Custom port (host:container)
```

### Health Checks

The application includes automatic health checks:

```bash
# Check manually
curl -f http://localhost:5000/api/status

# Via Docker
docker inspect --format='{{.State.Health.Status}}' mailcow-alias-generator
```

### Production Deployment

#### 1. Secure Configuration

```yaml
# docker-compose.override.yml
services:
  mailcow-alias-generator:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'
    environment:
      - FLASK_ENV=production
    restart: always
```

#### 2. Reverse Proxy with Nginx

Uncomment the nginx service in [`docker-compose.yml`](docker-compose.yml:24):

```yaml
nginx:
  image: nginx:alpine
  container_name: mailcow-alias-nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./ssl:/etc/nginx/ssl:ro
  depends_on:
    - mailcow-alias-generator
  restart: unless-stopped
```

#### 3. Nginx Configuration

Create [`nginx.conf`](nginx.conf:1):

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server mailcow-alias-generator:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 4. Security

- **Non-root user**: Application runs with `appuser` user (UID 1000)
- **Read-only volumes**: Configuration is mounted read-only
- **Network isolation**: Uses dedicated Docker network
- **Resource limits**: Configurable memory and CPU limits

### Docker Maintenance

```bash
# Backup logs
docker cp mailcow-alias-generator:/app/logs ./backup-logs

# Update application
git pull
docker-compose build --no-cache
docker-compose up -d

# Clean unused images
docker system prune -f

# Monitor resources
docker stats mailcow-alias-generator
```

## � Security

### Recommendations

- **Protect your API key**: Never share it and store it securely
- **Network access**: Limit application access (firewall, VPN, etc.)
- **HTTPS**: Use a reverse proxy with SSL in production
- **Authentication**: Add an authentication layer if necessary

### Secure Deployment

For production use, consider:

1. **Nginx reverse proxy** with SSL
2. **Basic authentication** or OAuth
3. **IP restriction** if possible
4. **Environment variables** for sensitive configuration

## 🐛 Troubleshooting

### Common Errors

**"Invalid configuration"**
- Check that [`config.json`](config.json:1) exists and contains all required parameters
- Ensure the file is properly mounted in the Docker container

**"Unable to connect to Mailcow"**
- Check the Mailcow URL in the configuration
- Test network connectivity from the container
- Verify that the Mailcow API is enabled
- For Docker: verify that the container can access the external URL

**"API authentication error"**
- Check the API key in the configuration
- Make sure the key has the right permissions
- Test the API key directly with curl

**"This alias already exists"**
- The generated alias already exists, try with another service name

### Docker Troubleshooting

**Container won't start**
```bash
# Check startup logs
docker-compose logs mailcow-alias-generator

# Verify configuration
docker-compose config

# Rebuild image
docker-compose build --no-cache
```

**Permission issues**
```bash
# Check file permissions
ls -la config.json logs/

# Fix permissions if needed
chmod 644 config.json
chmod -R 755 logs/
```

**Container keeps restarting**
```bash
# Check health checks
docker inspect mailcow-alias-generator | grep -A 10 Health

# Temporarily disable health check
# Comment out healthcheck section in docker-compose.yml
```

**Network issues**
```bash
# Test connectivity from container
docker-compose exec mailcow-alias-generator curl -I https://your-mailcow.example.com

# Check Docker networks
docker network ls
docker network inspect mailcow-alias-generator_mailcow-alias-net
```

### Logs

#### Application Logs
```bash
# Via Docker Compose
docker-compose logs -f mailcow-alias-generator

# Logs inside container
docker-compose exec mailcow-alias-generator tail -f /app/logs/mailcow_alias.log

# Logs on host (if volume mounted)
tail -f ./logs/mailcow_alias.log
```

#### Available Logs
- [`logs/mailcow_alias.log`](logs/mailcow_alias.log:1): Application logs
- [`logs/alias_log.json`](logs/alias_log.json:1): Created aliases history

### API Testing

```bash
# Test connection (replace 5000 with your configured port)
curl http://localhost:5000/api/status

# Test from inside container
docker-compose exec mailcow-alias-generator curl http://localhost:5000/api/status

# Create a test alias
curl -X POST http://localhost:5000/api/create-alias \
  -H "Content-Type: application/json" \
  -d '{"alias": "test1234@example.com", "redirectTo": "user@example.com"}'
```

### Debug Mode

To enable debug mode:

```yaml
# In docker-compose.yml
environment:
  - FLASK_ENV=development
  - FLASK_DEBUG=1
```

Then restart:
```bash
docker-compose restart
```

## 📝 Usage Example

1. **Sign up for a new service** (e.g., Supabase)
2. **Open the interface**: `http://localhost:5000` (or your configured port)
3. **Enter**: `supabase`
4. **Generated preview**: `supabase6789@example.com`
5. **Click**: "Create Alias"
6. **Use the alias** for Supabase registration

Now, all emails from Supabase will arrive at `user@example.com` but you'll know they come from Supabase thanks to the alias!

## 🤝 Support

In case of problems:
1. Check the logs in `mailcow_alias.log`
2. Test the connection with `/api/status`
3. Verify the Mailcow configuration
4. Consult the Mailcow API documentation

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This means you can freely use, modify, and distribute this software, but any derivative works must also be licensed under GPL v3.0.