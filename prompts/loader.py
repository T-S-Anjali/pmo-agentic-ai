"""
Prompt loader — loads prompt templates from the /prompts directory.
"""
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "templates"


def load_prompt(name: str) -> str:
    """Load a prompt template by name (without .txt extension)."""
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")
