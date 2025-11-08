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
tp-python-EH/
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

