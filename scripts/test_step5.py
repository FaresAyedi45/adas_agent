import sys; sys.path.insert(0, 'C:/adas_agent')
from agent_core import detect_question_type, compute_confidence

tests = [
    ('C est quoi le AEB ?', 'definition'),
    ('Quelle norme ISO pour ASIL ?', 'norme'),
    ('Calcul du TTC a 80km/h distance 20m', 'calcul'),
    ('Pourquoi mon AEB ne fonctionne pas ?', 'diagnostic'),
]
ok = 0
for q, expected in tests:
    detected = detect_question_type(q)
    if detected == expected:
        ok += 1
        print(f'  OK: {q[:40]} -> {detected}')
    else:
        print(f'  FAIL: {q[:40]} -> {detected} (attendu: {expected})')

chunks_mock = [{'score': 0.75}, {'score': 0.82}, {'score': 0.68}]
conf = compute_confidence(chunks_mock)
assert 50 <= conf <= 100, f'Confiance hors plage: {conf}'
print(f'Score confiance: {conf}%')
print(f'STEP 5 OK: {ok}/4 types detectes, confiance={conf}%')
