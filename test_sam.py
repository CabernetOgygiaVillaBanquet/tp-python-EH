#!/usr/bin/env python3
"""
Script de test pour extraire la base SAM
DOIT être exécuté en tant qu'Administrateur !
"""
from Client import cmd_get_sam_database

print("="*60)
print("TEST D'EXTRACTION DE LA BASE SAM")
print("="*60)

result = cmd_get_sam_database()
print(result)

print("\n" + "="*60)
print("Vérifiez les fichiers créés:")
print("  - sam_export.hiv")
print("  - system_export.hiv")
print("="*60)
