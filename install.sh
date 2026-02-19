set -euo pipefail

REPO_URL="https://github.com/Skribb11es/homepage-nordvpn-widget"
INSTALL_DIR="/opt/nordvpn-status"
ENV_FILE="/etc/nordvpn-status.env"
SERVICE_FILE_SRC="nord-status-server.service"
SERVICE_FILE_DST="/etc/systemd/system/nord-status-server.service"

echo "== NordVPN Homepage Widget Installer =="

if [[ "$EUID" -ne 0 ]]; then
  echo "ERROR: Please run as root (sudo ./install.sh)"
  exit 1
fi

echo "[1/7] installing python..."
apt update
apt install -y git python3 curl

echo "[2/7] installing Flask..."
apt install python3-flask

TMP_DIR="$(mktemp -d)"
echo "[3/7] cloning into $TMP_DIR ..."
git clone "$REPO_URL" "$TMP_DIR"

if [[ ! -f "$TMP_DIR/server.py" ]]; then
  echo "ERROR: server.py not found in repo root!"
  exit 1
fi

if [[ ! -f "$TMP_DIR/$SERVICE_FILE_SRC" ]]; then
  echo "ERROR: $SERVICE_FILE_SRC not found in repo root!"
  exit 1
fi

echo "[4/7] moving server.py into $INSTALL_DIR ..."
mkdir -p "$INSTALL_DIR"
cp -f "$TMP_DIR/server.py" "$INSTALL_DIR/server.py"
chmod +x "$INSTALL_DIR/server.py"

echo "[5/7] creating env file in $ENV_FILE ..."
if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<EOF
EOF
  chmod 600 "$ENV_FILE"
  echo "Created $ENV_FILE"
else
  echo "$ENV_FILE already exists."
fi

echo "[6/7] setting up systemd service..."
cp -f "$TMP_DIR/$SERVICE_FILE_SRC" "$SERVICE_FILE_DST"

systemctl daemon-reload
systemctl enable nord-status-server.service

rm -rf "$TMP_DIR"

echo "[7/7] finished!"
echo
echo "Service status:"
systemctl status nord-status-server.service --no-pager || true