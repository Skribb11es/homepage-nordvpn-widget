import subprocess
import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

API_TOKEN = os.environ.get("NORDVPN_STATUS_TOKEN", "").strip()

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
    except Exception as e:
        return ""

def parse_nordvpn_status(raw: str):
    data = {
        "connected": False,
        "status": "unknown",
        "hostname": None,
        "ip": None,
        "country": None,
        "city": None,
        "technology": None,
        "protocol": None,
        "transfer": None,
        "uptime": None,
        "raw": raw,
    }

    if not raw:
        data["status"] = "error"
        return data

    for line in raw.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip().lower()
        v = v.strip()

        # kinda crap way to do this, but it works and its currently 3am
        if k == "status":
            data["status"] = v.lower()
            data["connected"] = ("connected" in v.lower())
        elif k == "hostname":
            data["hostname"] = v
        elif k == "ip":
            data["ip"] = v
        elif k == "country":
            data["country"] = v
        elif k == "city":
            data["city"] = v
        elif k == "current technology":
            data["technology"] = v
        elif k == "current protocol":
            data["protocol"] = v
        elif k == "transfer":
            data["transfer"] = v
        elif k == "uptime":
            data["uptime"] = v

    return data

def check_auth():
    if not API_TOKEN:
        return True

    header = request.headers.get("Authorization", "")
    token_qs = request.args.get("token", "")

    if header.startswith("Bearer "):
        tok = header.replace("Bearer ", "", 1).strip()
        return tok == API_TOKEN

    return token_qs.strip() == API_TOKEN

def get_iface_ipv4(iface="eth0" if not os.environ.get("NORDVPN_STATUS_IFACE") else os.environ.get("NORDVPN_STATUS_IFACE")):
    try:
        out = subprocess.check_output(
            ["bash", "-lc", f"ip -4 addr show {iface} | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){{3}}' | head -n1"],
            text=True
        ).strip()
        return out if out else None
    except Exception:
        return None

@app.route("/status", methods=["GET"])
def status():
    if not check_auth():
        abort(401)

    raw = run_cmd(["/usr/bin/nordvpn", "status"])
    parsed = parse_nordvpn_status(raw)

    public_ip = run_cmd(["bash", "-lc", "curl -s --max-time 2 https://api.ipify.org || true"])
    if public_ip:
        parsed["public_ip_check"] = public_ip

    return jsonify(parsed)

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "nord-status-server",
        "endpoints": ["/status"]
    })

if __name__ == "__main__":
    bind_ip = get_iface_ipv4("eth0") or "0.0.0.0"
    app.run(host=bind_ip, port=8787)