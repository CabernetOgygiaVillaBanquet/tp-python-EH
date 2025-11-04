import asyncio
import json
import logging
import platform
import os
import psutil
import websockets
from common import make_hmac, timestamp, json_safe_loads

SERVER = "ws://<IP du serveur>:8765"  # Pense à bien remplacer ça par l'ip de ta machine serveur nico/prof

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("simpleagent")

def get_non_loopback_ips():
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            try:
                fam = a.family.name
            except Exception:
                fam = str(a.family)
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
            depth = root[len(path):].count(os.sep) if path != "/" else root.count(os.sep)
            result.append(root + ":")
            for d in dirs:
                result.append("  <dir> " + d)
            for f in files:
                result.append("  " + f)
            if depth >= max_depth:
                dirs[:] = []
        return "\n".join(result) if result else "(empty)"
    except PermissionError:
        return "(permission denied)"
    except FileNotFoundError:
        return "(path not found)"
    except Exception as e:
        return f"(error: {e})"

def cmd_uptime():
    try:
        with open("/proc/uptime") as f:
            up = float(f.readline().split()[0])
            hours = int(up // 3600)
            mins = int((up % 3600) // 60)
            return f"up {hours}h {mins}m (from /proc/uptime)"
    except Exception:
        return "(uptime not available)"

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
                    else:
                        out = f"(command '{name}' not allowed)"
                    reply = {"id": cid, "status": "ok", "output": out}
                    await ws.send(json.dumps(reply))
        except Exception as e:
            logger.warning("Erreur ou déconnexion: %s — reconnexion dans 5s", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_agent())