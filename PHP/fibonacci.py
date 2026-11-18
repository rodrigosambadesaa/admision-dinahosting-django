#!/usr/bin/env python3
"""Ejecución CLI del ejercicio 1 desde la estructura de entrega exigida en el PDF.

Es una reimplementación nativa en Django/Python; NO incluye código PHP de la
solución original. La lógica vive en challenge.services y el comando de Django.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.management import execute_from_command_line  # noqa: E402

if __name__ == "__main__":
    execute_from_command_line(["manage.py", "fibonacci", *sys.argv[1:]])
