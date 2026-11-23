import sys; sys.path.insert(0, 'C:/adas_agent')
from memory_manager import save_exchange, load_memory, get_memory_summary, clear_memory, get_memory_count
clear_memory()
for i in range(7):
    save_exchange(f'Question {i+1}', f'Réponse {i+1}', 'Ingénieur')
mem = load_memory()
assert len(mem) == 5, f'Attendu 5, got {len(mem)}'
assert 'Question 3' in mem[0]['question'], f'Premier: {mem[0]["question"]}'
assert 'Question 7' in mem[-1]['question'], f'Dernier: {mem[-1]["question"]}'
summary = get_memory_summary()
assert bool(summary)
clear_memory()
assert get_memory_count() == 0
print('STEP 3 OK: memory_manager fonctionne, fenêtre glissante correcte')
