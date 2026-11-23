# -*- coding: utf-8 -*-
import sys, re

def detect_user_persona(question: str):
    q_low = question.lower()
    
    # 1. Signaux Expert
    expert_keywords = [
        "corner case", "sotif vs", "iso 26262 vs", "jacobienne", "ekf", "filtre de kalman étendu",
        "insatisfaction", "limite physique", "faux positif", "zone 3", "zone 1",
        "redondance lockstep", "mc/dc", "subtilité", "différence majeure entre"
    ]
    if any(k in q_low for k in expert_keywords):
        return "Expert", "Analyse de cas limites et comparaisons théoriques poussées"

    # 2. Signaux Étudiant
    student_keywords = [
        "c'est quoi", "qu'est-ce", "expliqu", "débutant", "simple", "simplement",
        "c est quoi", "cest quoi", "vulgaris", "exemple simple", "à quoi sert", "comment ça marche"
    ]
    has_heavy_acronyms = any(k in q_low for k in ["asil", "hara", "iso 26262", "sotif", "hil", "sil", "mil", "can fd"])
    if any(k in q_low for k in student_keywords) and not has_heavy_acronyms:
        return "Étudiant", "Question conceptuelle d'initiation ou demande de vulgarisation"

    # 3. Signaux Ingénieur
    return "Ingénieur", "Terminologie d'ingénierie automobile et exigences normatives"

tests = [
    ("C est quoi le radar en automobile ?", "Étudiant"),
    ("Explique-moi l ACC simplement avec un exemple", "Étudiant"),
    ("Quel niveau ASIL pour l AEB selon l ISO 26262 et paramètres HARA ?", "Ingénieur"),
    ("Calcul du TTC seuil de freinage NHTSA pour poids lourds", "Ingénieur"),
    ("Quelle est la différence majeure entre un filtre de Kalman standard et un EKF ?", "Expert"),
    ("SOTIF vs ISO 26262 : analyse des corner cases en zone 3", "Expert"),
]

for q, expected in tests:
    res, reason = detect_user_persona(q)
    status = "OK" if res == expected else f"FAIL (got {res})"
    print(f"[{status}] '{q[:45]}' -> {res} ({reason})")
