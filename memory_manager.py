# -*- coding: utf-8 -*-
"""
Gestionnaire de Mémoire Conversationnelle — ADAS AI Agent
Fenêtre glissante : 5 échanges maximum
Auteurs : Selim Ghouaiel & Fares Ayedi
"""

import json
import os
from datetime import datetime
from typing import List, Dict

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory", "session_memory.json")
MAX_EXCHANGES = 5

def _ensure_memory_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def load_memory() -> List[Dict]:
    _ensure_memory_dir()
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_exchange(question: str, answer: str, persona: str):
    _ensure_memory_dir()
    memory = load_memory()
    exchange = {
        "timestamp": datetime.now().isoformat(),
        "persona": persona,
        "question": question[:300],
        "answer": answer[:500]
    }
    memory.append(exchange)
    if len(memory) > MAX_EXCHANGES:
        memory = memory[-MAX_EXCHANGES:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def get_memory_summary() -> str:
    memory = load_memory()
    if not memory:
        return ""
    lines = []
    for i, exchange in enumerate(memory, 1):
        q = exchange.get("question", "")
        a = exchange.get("answer", "")[:200]
        persona = exchange.get("persona", "")
        lines.append(f"Échange {i} [{persona}] — Q: {q} | R: {a}...")
    return "\n".join(lines)

def get_memory_count() -> int:
    return len(load_memory())

def clear_memory():
    _ensure_memory_dir()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def get_memory_as_messages() -> List[Dict]:
    memory = load_memory()
    messages = []
    for exchange in memory:
        messages.append({"role": "user", "content": exchange.get("question", "")})
        messages.append({"role": "assistant", "content": exchange.get("answer", "")})
    return messages
