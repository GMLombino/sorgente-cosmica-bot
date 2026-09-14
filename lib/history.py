"""
Gestione dello storico delle frasi già pubblicate, per evitare ripetizioni.
Il file history.json viene letto e riscritto ad ogni esecuzione, e va
committato nel repo GitHub così persiste tra un'esecuzione e l'altra
di GitHub Actions (i runner non hanno stato persistente di default).
"""
import json
import os
from datetime import datetime, timezone


def load_history(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_history(path: str, history: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_entry(path: str, frase: str, tema: str) -> None:
    history = load_history(path)
    history.append(
        {
            "frase": frase,
            "tema": tema,
            "data": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_history(path, history)


def recent_phrases(path: str, limit: int) -> list:
    history = load_history(path)
    return [entry["frase"] for entry in history[-limit:]]


def is_duplicate(path: str, frase: str) -> bool:
    history = load_history(path)
    frase_norm = frase.strip().lower()
    return any(entry["frase"].strip().lower() == frase_norm for entry in history)
