# -*- coding: utf-8 -*-
"""
ADAS AI Agent — Interface Streamlit Cockpit Haute Précision
ReAct · Mémoire Conversationnelle · Multi-Personas · Citations Inline Automotive
Développé par Selim Ghouaiel & Fares Ayedi
"""

import os
import sys
import re
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────
# BOOTSTRAP ENVIRONNEMENT (VENV AUTO-DÉTECTION)
# ──────────────────────────────────────────────────────
_venv_site = os.path.join("C:\\chatbot_adas", "venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

import streamlit as st
from prompt_manager import get_system_prompt, get_persona_list, get_persona_icon, get_persona_description
from memory_manager import save_exchange, get_memory_summary, get_memory_count, clear_memory, get_memory_as_messages
from agent_core import run_react_cycle
from rag_engine import get_db_stats

# ──────────────────────────────────────────────────────
# CONFIGURATION PAGE
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="ADAS AI Agent — Cockpit ReAct & Normes",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────
# NOMS LISIBLES DES DOCUMENTS TECHNIQUES (ALIASES)
# ──────────────────────────────────────────────────────
FILENAME_ALIASES = {
    "adas_2.pdf": "Complément ADAS — Niveau Débutant",
    "ADAS_Base_Connaissances.pdf": "Base de Connaissances ADAS",
    "Heavy Vehicle Automatic Emergency Braking.pdf": "AEB Véhicules Lourds — NHTSA/FMCSA",
    "Measurable Safety of Automated Driving Functions in Commercial Motor Vehicles - Technological and Methodical Approaches.pdf": "Sécurité Mesurable — Conduite Automatisée",
    "Self-Learning Longitudinal Control for On-Road Vehicles.pdf": "Contrôle Longitudinal Adaptatif (RL)",
    "ADAS_Ingenierie_Systemes_Normes_et_Validation.pdf": "Manuel d'Expertise ADAS — Normes, Réseaux & SOTIF",
}

def get_alias(raw_filename: str) -> str:
    clean_name = os.path.basename(raw_filename)
    return FILENAME_ALIASES.get(clean_name, clean_name)

# ──────────────────────────────────────────────────────
# CITATIONS INLINE HAUTE PRÉCISION (VERSION FINALE CHATBOT ADAS)
# ──────────────────────────────────────────────────────
def clean_latex_delimiters(text: str) -> str:
    """
    Corrige automatiquement les formules mathématiques mal délimitées
    (ex: \(...\) ou parenthèses entourant des commandes LaTeX comme \text, \frac, \sqrt)
    pour que Streamlit / KaTeX les affiche sous forme d'équations mathématiques nettes.
    """
    if not text:
        return text
    # Remplacer \( ... \) et \[ ... \]
    s = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    s = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', s, flags=re.DOTALL)
    # Remplacer toute parenthèse entourant du code LaTeX brut (\...) par des dollars $...$
    s = re.sub(r'\(([^()\n]*\\[a-zA-Z]+[^()\n]*)\)', r'$\1$', s)
    return s

def format_citations(text: str) -> str:
    """
    Substitue les citations documentaires comme [Heavy Vehicle Automatic Emergency Braking.pdf, Page 41]
    ou [Base de Connaissances ADAS, Page 1] en badges haute visibilité.
    """
    if not text:
        return text

    pattern = re.compile(
        r'\[(.+?),\s*([pP]ages?[\s\u00a0\u202f]+[\d\s\u00a0\u202f,–\-]+)\]'
    )

    def _replace_match(m):
        raw_doc = m.group(1).strip()
        raw_pg = m.group(2).strip().replace('\u00a0', ' ').replace('\u202f', ' ')
        alias = get_alias(raw_doc)

        svg_icon = (
            '<svg class="adas-cite-svg" viewBox="0 0 24 24" width="12" height="12" fill="none" '
            'stroke="#090d16" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
            '<polyline points="14 2 14 8 20 8"></polyline></svg>'
        )

        return (
            f'<span class="adas-cite-pill" title="Source technique : {alias}">'
            f'{svg_icon}'
            f'<span class="adas-cite-doc">{alias}</span>'
            f'<span class="adas-cite-sep">,</span>'
            f'<span class="adas-cite-page">{raw_pg}</span>'
            f'</span>'
        )

    return pattern.sub(_replace_match, text)

def format_display_text(text: str) -> str:
    """Combine le nettoyage LaTeX et le formatage des citations haute précision."""
    return format_citations(clean_latex_delimiters(text))

# ──────────────────────────────────────────────────────
# RENDU DES SOURCES GROUPÉES (CARTE SOURCE EXPANDABLE)
# ──────────────────────────────────────────────────────
def render_sources(sources: list):
    """Affiche les extraits de sources groupés sous chaque réponse."""
    if not sources:
        return

    grouped = {}
    for c in sources:
        alias = c.get("alias", c.get("source", "Inconnu"))
        page = c.get("page", 1)
        content = c.get("content", "")
        if alias not in grouped:
            grouped[alias] = {"pages": set(), "excerpts": []}
        grouped[alias]["pages"].add(page)
        if len(grouped[alias]["excerpts"]) < 2:
            clean_excerpt = content.strip().replace("\n", " ")
            if len(clean_excerpt) > 230:
                clean_excerpt = clean_excerpt[:230] + "..."
            grouped[alias]["excerpts"].append(clean_excerpt)

    n = len(grouped)
    plural = "s" if n > 1 else ""
    with st.expander(f"📂 Dossiers Documentaires RAG ({n} fichier{plural})", expanded=False):
        for alias, data in grouped.items():
            pages = sorted(data["pages"])
            excerpt = data["excerpts"][0] if data["excerpts"] else ""
            badges = "".join(f"<span class='page-badge'>Page {p}</span>" for p in pages)
            st.markdown(f"""
<div class='source-card'>
  <div class='source-title'>{alias}</div>
  <div class='pages-row'>{badges}</div>
  <div class='source-excerpt'>{excerpt}</div>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# FEUILLE DE STYLE AUTOMOTIVE HUD & HAUT CONTRASTE
# ──────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── FOND & TYPOGRAPHIE GLOBALE ── */
  .stApp {
      background: #f0f2f6;
      color: #1c1c2e;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  .stMarkdown, p, li, span, label { color: #1c1c2e; }
  h1, h2, h3 { color: #0d1b2a; font-weight: 750; }

  /* ── SIDEBAR INSTRUMENTATION AUTOMOTIVE ── */
  [data-testid="stSidebar"] {
      background: #e6e9f2;
      border-right: 1px solid #c8cde0;
  }

  /* ── BULLES DE CONVERSATION HUD ── */
  div[data-testid="stChatMessage"]:has([data-testid="stAvatar"][aria-label="user"]) {
      background: #dbeafe;
      border: 1px solid #93c5fd;
      border-radius: 14px;
      padding: 14px 18px;
      margin-bottom: 12px;
      box-shadow: 0 1px 4px rgba(37, 99, 235, 0.05);
  }

  div[data-testid="stChatMessage"]:has([data-testid="stAvatar"][aria-label="assistant"]) {
      background: #ffffff;
      border: 1px solid #d8dcea;
      border-radius: 14px;
      padding: 16px 20px;
      margin-bottom: 14px;
      box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
  }

  /* ── BARRE DE SAISIE MODERNE COCKPIT ── */
  [data-testid="stChatInput"] {
      background: #ffffff !important;
      border: 2px solid #aab4cc !important;
      border-radius: 20px !important;
      box-shadow: 0 3px 14px rgba(15, 23, 42, 0.07) !important;
      padding: 3px 12px !important;
      transition: all 0.25s ease;
  }
  [data-testid="stChatInput"]:focus-within {
      border-color: #2563eb !important;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15), 0 4px 16px rgba(37, 99, 235, 0.12) !important;
  }
  [data-testid="stChatInput"] textarea {
      background: transparent !important;
      color: #0f172a !important;
      font-size: 0.96rem;
      border: none !important;
  }
  [data-testid="stChatInput"] textarea::placeholder {
      color: #64748b !important;
  }

  /* ── CITATIONS INLINE HAUTE PRÉCISION ── */
  .adas-cite-pill {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 1px 7px;
      margin: 1px 3px;
      vertical-align: baseline;
      font-size: 0.85em;
      line-height: 1.45;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
      white-space: nowrap;
      transition: all 0.2s ease;
  }
  .adas-cite-pill:hover {
      background: #e2e8f0;
      border-color: #94a3b8;
  }
  .adas-cite-svg {
      flex-shrink: 0;
      vertical-align: -1px;
  }
  .adas-cite-doc {
      color: #090d16 !important;
      font-weight: 750 !important;
      letter-spacing: -0.01em;
  }
  .adas-cite-sep {
      color: #94a3b8;
      font-weight: 600;
  }
  .adas-cite-page {
      color: #3b0764 !important;
      background: #fae8ff;
      border: 1px solid #e879f9;
      border-radius: 4px;
      padding: 0 6px;
      font-weight: 800 !important;
      letter-spacing: 0.01em;
  }

  /* ── CARTES SOURCES GROUPÉES ── */
  .source-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 12px 14px;
      margin-bottom: 8px;
  }
  .source-title {
      font-weight: 750;
      color: #090d16;
      font-size: 0.92rem;
      margin-bottom: 6px;
  }
  .pages-row { margin-bottom: 6px; }
  .page-badge {
      display: inline-block;
      background: #fae8ff;
      color: #3b0764 !important;
      border: 1px solid #e879f9;
      font-size: 0.72rem;
      font-weight: 800;
      border-radius: 4px;
      padding: 1px 8px;
      margin: 0 4px 4px 0;
  }
  .source-excerpt {
      font-size: 0.81em;
      color: #334155;
      font-style: italic;
      background: #f1f5f9;
      border-left: 3px solid #2563eb;
      padding: 6px 10px;
      border-radius: 0 6px 6px 0;
      margin-top: 6px;
      line-height: 1.5;
  }

  /* ── ÉTAPES DU CYCLE REACT ── */
  .react-step-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #2563eb;
      border-radius: 8px;
      padding: 8px 12px;
      margin: 4px 0;
      font-size: 0.88rem;
      line-height: 1.45;
  }
  .step-think  { border-left-color: #f59e0b !important; background: #fffbeb !important; }
  .step-search { border-left-color: #10b981 !important; background: #ecfdf5 !important; }
  .step-reason { border-left-color: #8b5cf6 !important; background: #f5f3ff !important; }
  .step-memory { border-left-color: #ec4899 !important; background: #fdf2f8 !important; }

  /* ── BADGES & GOUVERNANCE ── */
  .conf-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 12px;
      border-radius: 14px;
      font-weight: 750;
      font-size: 0.82rem;
  }
  .conf-high { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
  .conf-med  { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
  .conf-low  { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

  .persona-badge {
      display: inline-block;
      background: #dbeafe;
      color: #1e40af;
      border: 1px solid #93c5fd;
      padding: 3px 12px;
      border-radius: 16px;
      font-weight: 750;
      font-size: 0.83rem;
  }

  /* ── HEADER HUD COCKPIT ── */
  .adas-header-hud {
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 60%, #eef2f6 100%);
      border: 1px solid #d8dce8;
      border-radius: 16px;
      padding: 18px 24px;
      margin-bottom: 20px;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# SIDEBAR INSTRUMENTATION
# ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚗 ADAS AI Agent")
    st.markdown("*Architecture ReAct · Mémoire 5 Tours · Multi-Personas*")
    st.divider()

    st.markdown("### 👥 Gouvernance du Profil")
    personas_options = ["Auto-Détection 🎯"] + get_persona_list()
    selected_persona = st.radio(
        "Mode d'attribution du rôle :",
        personas_options,
        format_func=lambda p: "🎯 Détection Autonome (ReAct)" if p.startswith("Auto") else f"{get_persona_icon(p)} {p}",
        index=0,
        key="persona_selector"
    )
    if selected_persona.startswith("Auto"):
        st.info("*L'agent analyse l'intention et la technicité dans le cycle ReAct, déduit votre rôle (Étudiant/Ingénieur/Expert) et adapte son Prompt Manager en temps réel.*")
    else:
        st.info(f"*{get_persona_description(selected_persona)}*")
    st.divider()

    st.markdown("### 💾 Mémoire Conversationnelle")
    mem_count = get_memory_count()
    st.metric("Tours mémorisés", f"{mem_count} / 5", help="Fenêtre glissante conservant les 5 derniers échanges pour le suivi de contexte")
    if mem_count > 0:
        with st.expander("Consulter l'état de la mémoire"):
            summary = get_memory_summary()
            st.text(summary[:600] + "..." if len(summary) > 600 else summary)
        if st.button("🗑️ Effacer la mémoire", use_container_width=True):
            clear_memory()
            st.rerun()
    st.divider()

    st.markdown("### 📚 Base Documentaire ADAS")
    try:
        stats = get_db_stats()
        st.metric("Chunks indexés (ChromaDB)", stats["total_chunks"])
        for doc in [
            "Base de Connaissances ADAS",
            "Manuel d'Expertise ADAS & Normes",
            "AEB Véhicules Lourds (NHTSA)",
            "Sécurité Mesurable ADAS",
            "Contrôle Longitudinal (RL)",
            "Complément ADAS Débutant"
        ]:
            st.markdown(f"  • {doc}")
    except Exception:
        st.warning("Base non connectée.")
    st.divider()
    st.caption("Auteurs : Selim Ghouaiel & Fares Ayedi")

# ──────────────────────────────────────────────────────
# HEADER COCKPIT HUD
# ──────────────────────────────────────────────────────
active_display = "🎯 Détection Autonome (Classification en direct)" if selected_persona.startswith("Auto") else f"{get_persona_icon(selected_persona)} Mode {selected_persona}"
st.markdown(f"""
<div class="adas-header-hud">
    <div style="font-size: 1.5rem; font-weight: 800; color: #0d1b2a; display: flex; align-items: center; gap: 10px;">
        <span>🚗</span> ADAS AI Agent — Ingénierie & Sûreté Fonctionnelle
    </div>
    <div style="color: #475569; font-size: 0.90rem; margin-top: 4px;">
        Agent Cognitif ReAct · Mémoire 5 Tours · Multi-Personas · Base Normative ISO 26262 & SOTIF
    </div>
    <div style="margin-top: 10px;">
        <span class="persona-badge">{active_display}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# HISTORIQUE DES MESSAGES
# ──────────────────────────────────────────────────────
if "ui_history" not in st.session_state:
    st.session_state.ui_history = []

for entry in st.session_state.ui_history:
    with st.chat_message("user"):
        st.markdown(entry["question"])
    with st.chat_message("assistant"):
        with st.expander("🧠 Raisonnement ReAct", expanded=False):
            for step in entry.get("steps", []):
                st.markdown(f"**{step['label']}** {step['content']}")
        st.markdown(format_display_text(entry["answer"]), unsafe_allow_html=True)
        if entry.get("sources"):
            render_sources(entry["sources"])
        conf = entry.get("confidence", 0)
        cls = "conf-high" if conf >= 70 else "conf-med" if conf >= 40 else "conf-low"
        st.markdown(
            f"<div style='margin-top: 8px;'>"
            f"<span class='conf-badge {cls}'>📊 Confiance : {conf}%</span> "
            f"<span class='persona-badge'>{get_persona_icon(entry['persona'])} {entry['persona']}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

# ──────────────────────────────────────────────────────
# SAISIE UTILISATEUR & STREAMING REACT
# ──────────────────────────────────────────────────────
input_hint = "Posez une question technique, normative ou conceptuelle ADAS..." if selected_persona.startswith("Auto") else f"Posez votre question ({get_persona_icon(selected_persona)} Mode {selected_persona})..."
user_input = st.chat_input(input_hint)

if user_input and user_input.strip():
    question = user_input.strip()

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        react_container = st.expander("🧠 Raisonnement ReAct", expanded=True)
        answer_placeholder = st.empty()
        sources_placeholder = st.empty()

        memory_summary = get_memory_summary()
        memory_messages = get_memory_as_messages()

        react_steps = []
        full_answer = ""
        confidence = 0
        answer_tokens = []
        retrieved_sources = []
        active_persona_used = "Ingénieur" if selected_persona.startswith("Auto") else selected_persona

        step_labels = {
            "think":         "🟡 PENSER & CLASSIFIER :",
            "search":        "🟢 CHERCHER :",
            "search_result": "🟢 RÉSULTATS :",
            "reason":        "🟣 RAISONNER :",
            "memory":        "🩷 MÉMORISER :"
        }

        for event in run_react_cycle(question, selected_persona, "", memory_messages, memory_summary):
            step = event["step"]
            content = event["content"]
            data = event["data"]

            if "active_persona" in data:
                active_persona_used = data["active_persona"]

            if step in step_labels:
                label = step_labels[step]
                with react_container:
                    st.markdown(f"**{label}** {content}")
                react_steps.append({"label": label, "content": content})
                if step == "search_result":
                    confidence = data.get("confidence", 0)
                    retrieved_sources = data.get("chunks", [])

            elif step == "answer_token":
                answer_tokens.append(content)
                current_text = "".join(answer_tokens)
                answer_placeholder.markdown(format_display_text(current_text) + "▌", unsafe_allow_html=True)

            elif step == "answer_done":
                full_answer = content
                confidence = data.get("confidence", confidence)
                retrieved_sources = data.get("sources", retrieved_sources)
                answer_placeholder.markdown(format_display_text(full_answer), unsafe_allow_html=True)

            elif step == "answer_error":
                answer_placeholder.error(content)
                full_answer = content

        # Rendu des sources groupées et badges
        if retrieved_sources:
            with sources_placeholder.container():
                render_sources(retrieved_sources)

        conf = confidence
        cls = "conf-high" if conf >= 70 else "conf-med" if conf >= 40 else "conf-low"
        auto_label = " (Auto-détecté)" if selected_persona.startswith("Auto") else ""
        st.markdown(
            f"<div style='margin-top: 8px;'>"
            f"<span class='conf-badge {cls}'>📊 Confiance : {conf}%</span> "
            f"<span class='persona-badge'>{get_persona_icon(active_persona_used)} {active_persona_used}{auto_label}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        if full_answer and "Erreur" not in full_answer:
            save_exchange(question, full_answer, active_persona_used)

        st.session_state.ui_history.append({
            "question": question,
            "answer": full_answer,
            "steps": react_steps,
            "confidence": confidence,
            "sources": retrieved_sources,
            "persona": active_persona_used
        })
        st.rerun()
