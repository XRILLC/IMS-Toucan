#!/bin/bash
# Installation script for IMS-Toucan TTS systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}IMS-Toucan TTS Service Installer${NC}"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Configuration
SERVICE_NAME="toucan-tts"
SERVICE_FILE="${SERVICE_NAME}.service"
INSTALL_DIR="/opt/ims-toucan"
USER="toucan"
GROUP="toucan"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}Error: ${SERVICE_FILE} not found in current directory${NC}"
    exit 1
fi

# Create user if doesn't exist
if ! id "$USER" &>/dev/null; then
    echo -e "${YELLOW}Creating user: $USER${NC}"
    useradd --system --home-dir "$INSTALL_DIR" --shell /bin/false "$USER"
else
    echo -e "${GREEN}User $USER already exists${NC}"
fi

# Create installation directory
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Creating installation directory: $INSTALL_DIR${NC}"
    mkdir -p "$INSTALL_DIR"
    chown "$USER:$GROUP" "$INSTALL_DIR"
else
    echo -e "${GREEN}Installation directory exists${NC}"
fi

# Create Models directory
mkdir -p "$INSTALL_DIR/Models"
chown "$USER:$GROUP" "$INSTALL_DIR/Models"

# Copy service file
echo -e "${YELLOW}Installing systemd service...${NC}"
cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_FILE"

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable service
echo -e "${YELLOW}Enabling ${SERVICE_NAME} service...${NC}"
systemctl enable "$SERVICE_NAME"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Install IMS-Toucan to $INSTALL_DIR:"
echo "   sudo -u $USER bash -c 'cd $INSTALL_DIR && python3 -m venv .venv && source .venv/bin/activate && pip install ims-toucan'"
echo ""
echo "2. Configure the service (edit /etc/systemd/system/${SERVICE_FILE}):"
echo "   - Change --device to 'cuda' if using GPU"
echo "   - Change --language for different default language"
echo "   - Adjust --port if needed"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "6. Test the API:"
echo '   curl -X POST "http://localhost:8000/synthesize" -H "Content-Type: application/json" -d '"'"'{"text": "Hello world", "language": "eng"}'"'"' --output test.wav'
echo ""
