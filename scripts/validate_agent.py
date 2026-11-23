# -*- coding: utf-8 -*-
"""
Validation finale ADAS AI Agent — 10 tests automatiques
Auteurs : Selim Ghouaiel & Fares Ayedi
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_core import detect_question_type, compute_confidence
from memory_manager import save_exchange, load_memory, clear_memory, get_memory_count
from prompt_manager import get_system_prompt, get_persona_list
from rag_engine import search, get_db_stats

PASS = 0
FAIL = 0

def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        print(f"  OK  [{label}] {detail}")
        PASS += 1
    else:
        print(f"  FAIL [{label}] {detail}")
        FAIL += 1

print("=" * 55)
print("VALIDATION ADAS AI AGENT")
print("=" * 55)

# T1 : ChromaDB
print("\n[T1] Base documentaire")
stats = get_db_stats()
check("ChromaDB chunks", stats["total_chunks"] > 100, f"{stats['total_chunks']} chunks")

# T2 : Personas
print("\n[T2] Personas")
personas = get_persona_list()
check("3 personas", len(personas) == 3, str(personas))
check("Ingénieur présent", "Ingénieur" in personas)

# T3 : Détection types
print("\n[T3] Détection types de questions")
tests_types = [
    ("C est quoi le AEB", "definition"),
    ("Quelle norme ISO pour ASIL", "norme"),
    ("Calcul TTC 80km/h 20m", "calcul"),
    ("Pourquoi AEB ne fonctionne pas", "diagnostic"),
]
ok_types = sum(1 for q, e in tests_types if detect_question_type(q) == e)
check("Types détectés", ok_types >= 3, f"{ok_types}/4")

# T4 : RAG search
print("\n[T4] Recherche RAG")
results = search("AEB freinage urgence norme", k=3)
check("Résultats RAG", len(results) > 0, f"{len(results)} résultats")
check("Alias présent", all("alias" in r for r in results))
check("Score présent", all("score" in r for r in results))

# T5 : Mémoire fenêtre glissante
print("\n[T5] Mémoire conversationnelle")
clear_memory()
for i in range(7):
    save_exchange(f"Question {i+1}", f"Réponse {i+1}", "Ingénieur")
mem = load_memory()
check("Fenêtre 5 max", len(mem) == 5, f"{len(mem)} échanges")
check("Glissement correct", "Question 3" in mem[0]["question"] if mem else False)

# T6 : Injection mémoire dans prompt
print("\n[T6] Injection mémoire dans le prompt")
p_sans = get_system_prompt("Ingénieur", "")
p_avec = get_system_prompt("Ingénieur", "test injection mémoire")
check("Mémoire injectée", "test injection mémoire" in p_avec)
check("Sans mémoire propre", "test injection mémoire" not in p_sans)

# T7 : Score confiance
print("\n[T7] Score de confiance")
high = compute_confidence([{"score": 0.85}, {"score": 0.90}, {"score": 0.78}])
low  = compute_confidence([{"score": 0.10}, {"score": 0.15}])
check("Confiance haute >= 70", high >= 70, f"{high}%")
check("Confiance haute > basse", high > low, f"{high}% > {low}%")

# T8 : Prompts distincts par persona
print("\n[T8] Différenciation prompts")
p_ing = get_system_prompt("Ingénieur")
p_etu = get_system_prompt("Étudiant")
p_exp = get_system_prompt("Expert")
check("3 prompts distincts", len({p_ing, p_etu, p_exp}) == 3)

# T9 : Reset mémoire
print("\n[T9] Reset mémoire")
clear_memory()
check("Mémoire effacée", get_memory_count() == 0)

# T10 : RAG pertinence ADAS
print("\n[T10] Pertinence RAG ADAS")
r2 = search("SOTIF ISO 21448 sécurité conduite autonome", k=2)
check("Pertinence SOTIF", len(r2) > 0 and r2[0]["score"] > 0.1)

print("\n" + "=" * 55)
print(f"RÉSULTAT FINAL : {PASS}/{PASS+FAIL} PASS")
if FAIL == 0:
    print("AGENT VALIDE - PRET POUR LA PRESENTATION")
else:
    print(f"ATTENTION : {FAIL} test(s) échoué(s)")
print("=" * 55)
