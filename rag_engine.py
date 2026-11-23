# -*- coding: utf-8 -*-
"""
Moteur RAG — ADAS AI Agent
ChromaDB + Sentence-Transformers (all-MiniLM-L6-v2)
Auteurs : Selim Ghouaiel & Fares Ayedi
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

_venv_site = os.path.join("C:\\chatbot_adas", "venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDFS_DIR = os.path.join(BASE_DIR, "data", "pdfs")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

FILENAME_ALIASES = {
    "adas_2.pdf": "Complément ADAS — Niveau Débutant",
    "ADAS_Base_Connaissances.pdf": "Base de Connaissances ADAS",
    "Heavy Vehicle Automatic Emergency Braking.pdf": "AEB Véhicules Lourds — NHTSA/FMCSA",
    "Measurable Safety of Automated Driving Functions in Commercial Motor Vehicles - Technological and Methodical Approaches.pdf": "Sécurité Mesurable — Conduite Automatisée",
    "Self-Learning Longitudinal Control for On-Road Vehicles.pdf": "Contrôle Longitudinal Adaptatif (RL)",
    "ADAS_Ingenierie_Systemes_Normes_et_Validation.pdf": "Manuel Expertise ADAS — Normes & SOTIF",
}

_vectorstore = None
_embeddings = None

def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings

def build_vectordb():
    embeddings = _get_embeddings()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    all_docs = []
    pdf_files = [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDFS_DIR, pdf_file)
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            chunks = splitter.split_documents(pages)
            for chunk in chunks:
                chunk.metadata["source_file"] = pdf_file
                chunk.metadata["alias"] = FILENAME_ALIASES.get(pdf_file, pdf_file)
            all_docs.extend(chunks)
            print(f"  OK {pdf_file}: {len(chunks)} chunks")
        except Exception as e:
            print(f"  ERREUR {pdf_file}: {e}")
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print(f"ChromaDB cree: {len(all_docs)} chunks totaux")
    return vectorstore

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = _get_embeddings()
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )
    return _vectorstore

import re

# Dictionnaire d'expansion sémantique du domaine automobile ADAS
ADAS_EXPANSIONS = {
    "ACC": "régulateur de vitesse adaptatif adaptive cruise control",
    "AEB": "freinage urgence automatique autonomous emergency braking",
    "FCW": "alerte collision frontale forward collision warning",
    "LKA": "maintien de voie lane keeping assist",
    "LDW": "alerte franchissement involontaire ligne lane departure warning",
    "TTC": "time to collision temps avant collision",
    "ASIL": "ASIL ISO 26262 niveau intégrité sécurité HARA",
    "SOTIF": "SOTIF ISO 21448 sécurité du fonctionnement prévu",
    "GSR2": "GSR2 règlement européen équipements sécurité 2024",
    "ALKS": "ALKS niveau 3 conduite autonome autoroute UNECE R157",
}

def search(query: str, k: int = 6) -> list:
    """
    Recherche vectorielle multi-requêtes avec expansion sémantique ADAS
    pour garantir une couverture maximale des définitions, normes et calculs.
    """
    vs = get_vectorstore()
    
    clean_q = re.sub(r'^(?:uel\b)', 'quel', query.strip(), flags=re.I)
    queries = [clean_q]
    
    # Expansion de requêtes avec les synonymes techniques et termes complets
    expanded_terms = []
    for acronym, expansion in ADAS_EXPANSIONS.items():
        if re.search(r'\b' + acronym + r'\b', clean_q, re.I):
            expanded_terms.append(f"{acronym} {expansion}")
            
    if expanded_terms:
        queries.append(f"{clean_q} " + " ".join(expanded_terms))
        
    seen = set()
    combined = []
    for q in queries:
        try:
            results = vs.similarity_search_with_relevance_scores(q, k=k)
            for doc, score in results:
                h = doc.page_content[:100].strip()
                if h not in seen:
                    seen.add(h)
                    combined.append({
                        "content": doc.page_content,
                        "source": doc.metadata.get("source_file", "Inconnu"),
                        "alias": doc.metadata.get("alias", doc.metadata.get("source_file", "Inconnu")),
                        "page": doc.metadata.get("page", 0) + 1,
                        "score": round(float(score), 3)
                    })
        except Exception:
            pass
            
    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined[:k]

def get_db_stats() -> dict:
    vs = get_vectorstore()
    collection = vs._collection
    count = collection.count()
    return {"total_chunks": count, "db_path": CHROMA_DIR}
