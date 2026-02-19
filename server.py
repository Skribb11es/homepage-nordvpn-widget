import subprocess
import os
import re
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
            # parse strings like "1.45 GiB received, 486.08 MiB sent"
            transfer_str = v or ""
            # find segments like '1.45 GiB received' or '486.08 MiB sent'
            parts = re.findall(r'([\d\.]+\s*[A-Za-z]+)\s*(received|sent)', transfer_str, flags=re.IGNORECASE)
            received = sent = None
            for val, label in parts:
                if label.lower().startswith('received'):
                    received = val.strip()
                elif label.lower().startswith('sent'):
                    sent = val.strip()

            if received and sent:
                data["transfer"] = f"{received} \u2193 | {sent} \u2191"
            else:
                # fallback to original string if parsing didn't match
                data["transfer"] = transfer_str
        elif k == "uptime":
            # parse strings like "5 hours 55 minutes 29 seconds" -> HH:MM:SS
            uptime_str = v or ""
            matches = re.findall(r"(\d+)\s*(day|days|hour|hours|minute|minutes|second|seconds)", uptime_str, flags=re.IGNORECASE)
            days = hours = minutes = seconds = 0
            for num, unit in matches:
                n = int(num)
                unit = unit.lower()
                if unit.startswith("day"):
                    days = n
                elif unit.startswith("hour"):
                    hours = n
                elif unit.startswith("minute"):
                    minutes = n
                elif unit.startswith("second"):
                    seconds = n

            total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
            hh = total_seconds // 3600
            mm = (total_seconds % 3600) // 60
            ss = total_seconds % 60
            data["uptime"] = f"{hh:02}:{mm:02}:{ss:02}"

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