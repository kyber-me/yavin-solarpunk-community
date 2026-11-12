from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_SRC = PROJECT_ROOT / "src"
BASE_KNOWLEDGE_PATH = PROJECT_SRC / "agents" / "base_knowledge"
IDEALIZADOR_ACCESS_KEY_ENV = "IDEALIZADOR_ACCESS_KEY"
