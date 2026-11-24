# -*- coding: utf-8 -*-
"""
Moteur ReAct — ADAS AI Agent
Cycle : Penser -> Chercher -> Raisonner -> Répondre -> Mémoriser
Auteurs : Selim Ghouaiel & Fares Ayedi
"""

import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")
from typing import Generator, Dict, List

_venv_site = os.path.join("C:\\chatbot_adas", "venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from dotenv import load_dotenv
from groq import Groq

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

GROQ_API_KEYS = [
    os.getenv("GROQ_API_KEY", ""),
    os.getenv("GROQ_API_KEY_FALLBACK", "")
]
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_MODEL_FALLBACK = "openai/gpt-oss-20b"

def _get_groq_client() -> Groq:
    for key in GROQ_API_KEYS:
        if key and key.startswith("gsk_"):
            return Groq(api_key=key)
    raise ValueError("Aucune clé Groq valide.")

def detect_question_type(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["c'est quoi", "qu'est-ce", "définition", "signifie", "expliqu", "cest quoi", "c est quoi"]):
        return "definition"
    elif any(w in q for w in ["norme", "iso", "asil", "sotif", "unece", "réglementation", "standard", "regulation"]):
        return "norme"
    elif any(w in q for w in ["calcul", "formule", "ttc", "distance", "vitesse", "valeur", "seuil", "km/h"]):
        return "calcul"
    elif any(w in q for w in ["problème", "erreur", "défaillance", "diagnostic", "panne", "pourquoi ne", "ne fonctionne"]):
        return "diagnostic"
    else:
        return "general"

import re

def detect_user_persona(question: str) -> tuple:
    """
    Déduit de manière autonome le profil de l'interlocuteur à partir de la technicité
    et des intentions de sa question.
    Retourne (nom_persona, justification_raisonnement)
    """
    q_low = question.lower()
    
    # 1. Signaux Expert (questions de pointe, limites, nuances théoriques)
    expert_keywords = [
        "corner case", "sotif vs", "iso 26262 vs", "iso 21448 vs", "jacobienne", "ekf", "filtre de kalman étendu",
        "insatisfaction", "limite physique", "faux positif", "zone 3", "zone 1", "zone 2",
        "redondance lockstep", "mc/dc", "subtilité", "subtilite", "différence majeure", "difference majeure",
        "comparaison entre", "comparer iso", "cas limite", "mode expert", "expert"
    ]
    if any(k in q_low for k in expert_keywords):
        return "Expert", "analyse de cas limites et comparaisons théoriques pointues"

    # 2. Signaux Étudiant (questions introductives, vulgarisation, termes simples)
    student_keywords = [
        "c'est quoi", "qu'est-ce", "expliqu", "débutant", "simple", "simplement",
        "c est quoi", "cest quoi", "vulgaris", "exemple simple", "à quoi sert", "comment ça marche"
    ]
    has_heavy_acronyms = any(k in q_low for k in ["asil", "hara", "iso 26262", "sotif", "hil", "sil", "mil", "can fd"])
    if any(k in q_low for k in student_keywords) and not has_heavy_acronyms:
        return "Étudiant", "question conceptuelle d'initiation ou demande de vulgarisation"

    # 3. Signaux Ingénieur (terminologie technique standard, normes, calculs)
    return "Ingénieur", "terminologie d'ingénierie automobile et exigences normatives"

def build_rag_query(question: str, question_type: str) -> str:
    # Nettoie les coquilles courantes en conservant la précision sémantique
    q = question.strip()
    q = re.sub(r'^(?:uel\b)', 'Quel', q, flags=re.I)
    return q

def compute_confidence(chunks: List[Dict]) -> int:
    """
    Calcule un score de confiance (0-100%) dynamique basé sur :
    - Le score maximal de similarité cosinus (pertinence du meilleur chunk)
    - Le score moyen des chunks retournés
    Calibré pour all-MiniLM-L6-v2 sur ChromaDB.
    """
    if not chunks:
        return 0
    scores = [c.get("score", 0.0) for c in chunks]
    top_score = max(scores)
    avg_score = sum(scores) / len(scores)
    
    # Combinaison pondérée du meilleur chunk et de la moyenne
    base_conf = (top_score * 0.65 + avg_score * 0.35)
    
    # Échelle de mapping vers 0-100% :
    # Si base_conf >= 0.25 (très forte pertinence documentaire) -> 75% à 95%
    # Si base_conf ~ 0.10 -> ~50%
    # Si base_conf <= 0 (hors-sujet) -> <20%
    if base_conf > 0:
        scaled = int(35 + (base_conf / 0.30) * 55)
    else:
        scaled = int(max(5, 35 + base_conf * 100))
        
    return min(max(scaled, 5), 98)

def run_react_cycle(
    question: str,
    persona: str,
    system_prompt: str,
    memory_messages: List[Dict],
    memory_summary: str = ""
) -> Generator:
    from rag_engine import search
    from prompt_manager import get_system_prompt, get_persona_icon

    # ETAPE 1 : PENSER & PROFILER L'UTILISATEUR
    question_type = detect_question_type(question)
    
    if not persona or persona.startswith("Auto"):
        active_persona, persona_reason = detect_user_persona(question)
        icon = get_persona_icon(active_persona)
        profiling_msg = f"Rôle utilisateur déduit : **{icon} {active_persona}** ({persona_reason}).\nAdaptation autonome du Prompt Manager appliquée."
        system_prompt = get_system_prompt(active_persona, memory_summary)
    else:
        active_persona = persona
        icon = get_persona_icon(active_persona)
        profiling_msg = f"Mode rôle imposé par l'utilisateur : **{icon} {active_persona}**."
        if not system_prompt:
            system_prompt = get_system_prompt(active_persona, memory_summary)

    yield {
        "step": "think",
        "content": f"Type de question : **{question_type}** | {profiling_msg}",
        "data": {"question_type": question_type, "active_persona": active_persona}
    }
    time.sleep(0.2)

    # ETAPE 2 : CHERCHER
    rag_query = build_rag_query(question, question_type)
    yield {
        "step": "search",
        "content": f"Recherche dans la base documentaire ADAS...\nQuery : *\"{rag_query[:100]}\"*",
        "data": {"query": rag_query}
    }

    chunks = search(rag_query, k=6)
    confidence = compute_confidence(chunks)

    sources_text = "\n".join([
        f"  • [{c['alias']}, Page {c['page']}] — Score : {c['score']}"
        for c in chunks
    ])
    yield {
        "step": "search_result",
        "content": f"{len(chunks)} extraits trouvés :\n{sources_text}",
        "data": {"chunks": chunks, "confidence": confidence}
    }
    time.sleep(0.1)

    # ETAPE 3 : RAISONNER
    yield {
        "step": "reason",
        "content": f"Synthèse cognitive en mode **{get_persona_icon(active_persona)} {active_persona}** | Confiance documentaire : **{confidence}%**",
        "data": {"confidence": confidence, "persona": active_persona}
    }

    context = "\n\n---\n\n".join([
        f"[Source: {c['alias']}, Page {c['page']}]\n{c['content']}"
        for c in chunks
    ])
    if not context.strip():
        context = "Aucun document pertinent trouvé dans la base. Dis-le clairement."

    # ETAPE 4 : REPONDRE
    client = _get_groq_client()
    messages = [{"role": "system", "content": system_prompt}]
    messages += memory_messages
    messages.append({
        "role": "user",
        "content": f"""DOCUMENTS ADAS (base documentaire officielle) :
{context}

---

QUESTION : {question}

Réponds UNIQUEMENT à partir des documents ci-dessus. Cite tes sources avec [nom_document, Page X]."""
    })

    yield {"step": "answer_start", "content": "", "data": {}}

    full_answer = ""
    model_used = GROQ_MODEL
    try:
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.1,
            stream=True
        )
        for chunk_resp in stream:
            delta = chunk_resp.choices[0].delta.content or ""
            full_answer += delta
            yield {"step": "answer_token", "content": delta, "data": {}}
    except Exception as e1:
        # Fallback model
        try:
            stream = client.chat.completions.create(
                model=GROQ_MODEL_FALLBACK,
                messages=messages,
                max_tokens=1024,
                temperature=0.1,
                stream=True
            )
            model_used = GROQ_MODEL_FALLBACK
            for chunk_resp in stream:
                delta = chunk_resp.choices[0].delta.content or ""
                full_answer += delta
                yield {"step": "answer_token", "content": delta, "data": {}}
        except Exception as e2:
            error_msg = f"Erreur génération : {e2}"
            yield {"step": "answer_error", "content": error_msg, "data": {}}
            full_answer = error_msg

    yield {
        "step": "answer_done",
        "content": full_answer,
        "data": {"confidence": confidence, "sources": chunks, "model": model_used, "active_persona": active_persona}
    }

    # ETAPE 5 : MEMORISER
    yield {
        "step": "memory",
        "content": "Échange mémorisé dans la session.",
        "data": {}
    }
