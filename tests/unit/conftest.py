"""Configuração do pytest: adiciona o diretório de bibliotecas ao path."""
import sys
from pathlib import Path

LIBS = Path(__file__).resolve().parent.parent.parent / "libraries"
sys.path.insert(0, str(LIBS))
