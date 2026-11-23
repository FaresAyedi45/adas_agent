import sys; sys.path.insert(0, 'C:/adas_agent')
from rag_engine import search, get_db_stats
stats = get_db_stats()
assert stats['total_chunks'] > 100, f'Trop peu de chunks: {stats["total_chunks"]}'
print(f'Chunks: {stats["total_chunks"]}')
results = search('AEB seuil activation freinage urgence', k=3)
assert len(results) == 3
assert all('alias' in r and 'score' in r for r in results)
print(f'Recherche OK: {len(results)} resultats')
for r in results:
    print(f'  Score={r["score"]} | {r["alias"]} | Page {r["page"]}')
print('STEP 4 OK: rag_engine fonctionne')
