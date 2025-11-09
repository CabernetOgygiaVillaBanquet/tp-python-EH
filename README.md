# TP Python - Ethical Hacking

Projet de client-serveur pour l'administration à distance et tests de sécurité dans un cadre d'ethical hacking.

## ⚠️ Avertissement

**Ce projet est destiné uniquement à des fins éducatives et de recherche en cybersécurité.**  
L'utilisation de ces outils sur des systèmes sans autorisation explicite est illégale. Utilisez uniquement dans un environnement contrôlé (VM, lab).

---

## 📋 Description

Ce projet implémente une architecture client-serveur permettant l'administration et le contrôle à distance de machines (Windows/Linux) via WebSockets. Il utilise une authentification HMAC et supporte l'exécution de commandes à distance.

## 📁 Structure du Projet

```
# TP Python - Ethical Hacking - Client/Serveur

## Description
Projet de démonstration d'un agent client/serveur pour l'ethical hacking avec authentification HMAC et exécution de commandes à distance.

## Architecture

### Serveur (`Server.py`)
- ✅ Gestion du Socket (WebSocket)
- ✅ Multi-processus avec fork (2 workers par défaut)
- ✅ Interpréteur de commandes
- ✅ Gestion d'erreur complète
- ✅ Authentification HMAC

### Client (`Client.py`)
Agent compatible Windows et Linux avec les fonctionnalités suivantes :

#### Fonctionnalités Communes (Windows/Linux)
- ✅ Gestion d'erreur
- ✅ Récupération adresses IP (sans localhost)
- ✅ Démarrage automatique au boot de la VM
- ✅ Exécution de commandes Shell/PowerShell
- ✅ Gestion du Socket (connexion au serveur)
- ✅ Captures d'écran

#### Fonctionnalités Spécifiques Windows
- ✅ **Récupération de la base SAM** (`get_sam`) - Exporte SAM et SYSTEM (nécessite admin)
- ✅ **Ajout de clef de registre** (`add_registry`) - Crée/modifie des clefs dans regedit

#### Fonctionnalités Spécifiques Linux
- ✅ **Récupération /etc/passwd et /etc/shadow** (`get_passwd_shadow`)
- ✅ **Liste récursive de /root et /home** (`list_root_home`)

## Commandes Disponibles

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

## Installation

### Dépendances
```bash
# Windows et Linux
pip install websockets psutil mss
```

### Configuration
1. **Serveur** : Modifier `HOST` et `PORT` dans `Server.py` si nécessaire
2. **Client** : Modifier `SERVER` dans `Client.py` avec l'IP du serveur
3. **Secret** : La clef HMAC est dans `common.py` (SECRET_KEY)

## Utilisation

### Démarrer le serveur
```bash
python Server.py
```

### Démarrer le client
```bash
# Windows
python Client.py

# Linux (peut nécessiter sudo pour certaines commandes)
sudo python Client.py
```

## Exemples de Commandes Serveur

### Commande Windows - Récupération SAM
```python
{"id": 9, "cmd": "get_sam"}
```

### Commande Windows - Ajout Registre
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

### Commande Linux - Passwd/Shadow
```python
{"id": 11, "cmd": "get_passwd_shadow"}
```

### Commande Linux - Liste /root et /home
```python
{"id": 12, "cmd": "list_root_home"}
```

## Sécurité

⚠️ **AVERTISSEMENT** : Ce code est à des fins éducatives uniquement.
- N'utilisez jamais sur des systèmes sans autorisation
- Certaines fonctions nécessitent des privilèges élevés (admin/root)
- L'authentification HMAC utilise une clef partagée (à changer en production)

## Structure des Fichiers

```
tp-python-EH/
├── Client.py          # Agent client (Windows/Linux)
├── Server.py          # Serveur de commande et contrôle
├── common.py          # Fonctions partagées (HMAC, JSON, timestamp)
└── README.md          # Cette documentation
```

## Auteur
Projet TP - BIN A3 CYBER - Ethical Hacking
/
│
├── Server.py           # Serveur WebSocket multi-processus
├── Client.py           # Agent client
├── README.md          # Documentation
│
└── screens/           # Dossier des captures d'écran (créé automatiquement)
```

## 🎓 Objectifs Pédagogiques

Ce projet permet d'apprendre :

1. **Programmation réseau** : WebSockets, protocoles client-serveur
2. **Sécurité** : HMAC, authentification, validation des entrées
3. **Programmation système** : Commandes shell, fichiers système
4. **Multiprocessing** : Fork, workers parallèles
5. **Gestion d'erreurs** : Try/except, timeouts, logging
6. **Cross-platform** : Code compatible Windows/Linux

---

## ⚖️ Licence

Ce projet est destiné uniquement à des fins éducatives dans le cadre du cours d'Ethical Hacking.

**Ne pas utiliser sur des systèmes sans autorisation explicite.**

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre du BIN A3 CYBER - Ethical Hacking

