# IMS-Toucan TTS Systemd Service

This directory contains the systemd service configuration for running IMS-Toucan as a REST API microservice.

## Quick Start

```bash
# 1. Install the service (requires root)
sudo ./install-service.sh

# 2. Install IMS-Toucan in /opt/ims-toucan
sudo -u toucan bash -c '
  cd /opt/ims-toucan
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e /path/to/ims-toucan-source
'

# 3. Start the service
sudo systemctl start toucan-tts

# 4. Enable auto-start on boot
sudo systemctl enable toucan-tts

# 5. Check status
sudo systemctl status toucan-tts

# 6. View logs
sudo journalctl -u toucan-tts -f
```

## Testing the API

Once the service is running, test it with curl:

```bash
# Health check
curl http://localhost:8000/health

# List supported languages
curl http://localhost:8000/languages

# Synthesize speech
curl -X POST "http://localhost:8000/synthesize" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world", "language": "eng"}' \
     --output output.wav

# Synthesize with voice cloning
curl -X POST "http://localhost:8000/synthesize-with-reference" \
     -F "text=Hello world" \
     -F "language=eng" \
     -F "reference=@voice.wav" \
     --output output.wav
```

## Configuration

Edit `/etc/systemd/system/toucan-tts.service` to customize:

```ini
# Change device (CPU or CUDA)
ExecStart=/opt/ims-toucan/.venv/bin/toucan-serve --host 0.0.0.0 --port 8000 --device cuda --language eng

# Adjust resource limits
MemoryLimit=8G         # Increase for GPU usage
CPUQuota=400%          # Adjust based on CPU cores
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart toucan-tts
```

## Security

The service runs with restricted permissions:
- Dedicated user: `toucan` (no login)
- Read-only system access
- Private /tmp
- Resource limits (4GB RAM, 200% CPU by default)
- Only writable: `/opt/ims-toucan/Models` and `/tmp`

## API Endpoints

- **GET /**: API information
- **GET /health**: Health check
- **GET /languages**: List supported languages
- **POST /synthesize**: Generate speech (JSON body)
- **POST /synthesize-with-reference**: Generate speech with voice cloning (multipart/form-data)
- **GET /docs**: Interactive API documentation (Swagger UI)
- **GET /redoc**: API documentation (ReDoc)

## Logs

View logs with journalctl:

```bash
# Follow logs in real-time
sudo journalctl -u toucan-tts -f

# View recent logs
sudo journalctl -u toucan-tts -n 100

# Filter by time
sudo journalctl -u toucan-tts --since "1 hour ago"

# Filter by priority (error only)
sudo journalctl -u toucan-tts -p err
```

## Troubleshooting

### Service won't start

```bash
# Check service status
sudo systemctl status toucan-tts

# Check logs for errors
sudo journalctl -u toucan-tts -n 50

# Test manually
sudo -u toucan bash -c '
  cd /opt/ims-toucan
  source .venv/bin/activate
  toucan-serve --host 127.0.0.1 --port 8000
'
```

### Models not loading

Ensure the toucan user has access:
```bash
sudo chown -R toucan:toucan /opt/ims-toucan/Models
```

### Out of memory

Increase memory limit in service file:
```ini
MemoryLimit=8G
```

### Port already in use

Change port in service file:
```ini
ExecStart=... --port 8001 ...
```

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop toucan-tts
sudo systemctl disable toucan-tts

# Remove service file
sudo rm /etc/systemd/system/toucan-tts.service

# Reload systemd
sudo systemctl daemon-reload

# Optional: Remove installation directory
sudo rm -rf /opt/ims-toucan

# Optional: Remove user
sudo userdel toucan
```

## Integration Examples

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/synthesize",
    json={"text": "Hello world", "language": "eng"}
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### Bash

```bash
#!/bin/bash
TEXT="Hello from bash"
curl -X POST "http://localhost:8000/synthesize" \
     -H "Content-Type: application/json" \
     -d "{\"text\": \"$TEXT\", \"language\": \"eng\"}" \
     --output output.wav
```

### JavaScript (Node.js)

```javascript
const fs = require('fs');
const fetch = require('node-fetch');

async function synthesize(text, language = 'eng') {
    const response = await fetch('http://localhost:8000/synthesize', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, language})
    });

    const buffer = await response.buffer();
    fs.writeFileSync('output.wav', buffer);
}

synthesize('Hello from JavaScript');
```

## Production Deployment

For production use:

1. **Use HTTPS**: Put behind nginx/Apache with SSL
2. **Add authentication**: Implement API key middleware
3. **Rate limiting**: Add rate limiting to prevent abuse
4. **Monitoring**: Set up Prometheus/Grafana for metrics
5. **Load balancing**: Run multiple instances for high availability
6. **Resource tuning**: Adjust memory/CPU limits based on load
7. **Logging**: Send logs to centralized logging system
