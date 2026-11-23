# 🚗 ADAS AI Agent — Agent Conversationnel ReAct & Multi-Personas

> **Agent intelligent de raisonnement et de recherche documentaire dédié aux systèmes d'aide à la conduite (ADAS) et à la sécurité fonctionnelle automobile.**  
> **Auteurs :** Selim Ghouaiel & Fares Ayedi

---

## 📌 Présentation du Projet

Ce projet implémente un **Agent d'Intelligence Artificielle autonome** basé sur le paradigme **ReAct** (*Reasoning + Acting*), spécialement conçu pour l'ingénierie automobile et les systèmes ADAS (*Advanced Driver Assistance Systems*).

### Pourquoi un AI Agent plutôt qu'un simple Chatbot RAG ?

Contrairement à un chatbot classique qui génère directement une réponse sans transparence, cet agent :
1. **Raisonnement explicite (ReAct)** : Il décompose son travail en étapes visibles (Penser $\rightarrow$ Chercher $\rightarrow$ Raisonner $\rightarrow$ Répondre $\rightarrow$ Mémoriser).
2. **Profilage autonome** : Il analyse la question pour détecter automatiquement si l'utilisateur est un **Étudiant**, un **Ingénieur** ou un **Expert**, et sélectionne dynamiquement le persona adapté.
3. **Mémoire conversationnelle d'état** : Il conserve une fenêtre glissante des **5 derniers échanges**, permettant des questions de suivi fluides (*"et quelle est sa formule ?"*, *"peux-tu détailler le deuxième point ?"*).
4. **Expansion d'acronymes ADAS** : Il enrichit sémantiquement les requêtes techniques (ex. *ACC*, *AEB*, *ASIL*, *TTC*, *SOTIF*, *GSR2*) pour cibler les meilleurs passages normatifs.
5. **Score d'auto-évaluation & Anti-hallucination** : Il calcule un score de confiance documentaire (en %) et refuse d'inventer si l'information est absente de la base documentaire officielle.

---

## 🧠 Cycle de Raisonnement ReAct

Chaque interaction utilisateur traverse le cycle suivant :

```
[ Question Utilisateur ]
           │
           ▼
  🟡 1. PENSER ──────────────► Détection de l'intention & du Profil (Étudiant / Ingénieur / Expert)
           │
           ▼
  🟢 2. CHERCHER ────────────► RAG : Recherche sémantique ChromaDB + Expansion d'acronymes ADAS
           │
           ▼
  🟣 3. RAISONNER ───────────► Synthèse LLM guidée par le Prompt Manager + Injection de la mémoire
           │
           ▼
  🔵 4. RÉPONDRE ────────────► Affichage Cockpit HUD, Badges de sources cliquables & Formules LaTeX
           │
           ▼
  🩷 5. MÉMORISER ───────────► Enregistrement dans l'historique de session (fenêtre glissante 5 tours)
```

1. **🟡 PENSER** : Catégorise la question (*Définition, Norme/Réglementation, Formule, Architecture*) et identifie le persona cible.
2. **🟢 CHERCHER** : Interroge la base vectorielle ChromaDB contenant plus de 2000 segments normatifs indexés.
3. **🟣 RAISONNER** : Construit une réponse structurée en citant rigoureusement chaque document et page sous le format `[Nom du Document, Page X]`.
4. **🔵 RÉPONDRE** : Restitue la réponse avec des badges de citations élégants, des équations mathématiques KaTeX et la jauge de confiance.
5. **🩷 MÉMORISER** : Met à jour la mémoire active pour assurer la continuité contextuelle.

---

## 🎭 Gouvernance des Personas

L'agent adapte son niveau d'explication, son ton et sa rigueur mathématique selon le profil détecté :

| Persona | Cible | Style & Contenu |
|---|---|---|
| **🎓 Mode Étudiant** | Débutants, étudiants | Pédagogique, accessible, définitions claires, analogies imagées, formules expliquées pas à pas. |
| **👷 Mode Ingénieur** | Ingénieurs systèmes, concepteurs | Technique et direct, normes applicables (ISO, UNECE), formules cinématiques, limites opérationnelles. |
| **🔬 Mode Expert** | Spécialistes Sûreté / SOTIF | Rigueur maximale, analyse des risques HARA (S/E/C), ASIL D, redondance matérielle, couverture MC/DC 100%. |

---

## 📚 Base Documentaire Intégrée

L'agent s'appuie sur une base de connaissances officielle composée de 6 documents de référence :

1. **Base de Connaissances ADAS** : Principes généraux, capteurs (Radar, Caméra, LiDAR), fonctions ACC, AEB, LKA, BSD.
2. **ADAS Ingénierie Systèmes, Normes & Validation** : Norme ISO 26262, ISO 21448 (SOTIF), cycle en V, HARA, seuils TTC.
3. **Manuel d'Expertise ADAS — Normes, Réseaux & SOTIF** : Architecture calculateurs, réseaux CAN/CAN-FD/Ethernet, ASIL D.
4. **Heavy Vehicle Automatic Emergency Braking (NHTSA/FMCSA)** : Réglementation et essais de freinage d'urgence sur véhicules lourds.
5. **Measurable Safety of Automated Driving Functions (TUD)** : Métriques de sécurité et approches de validation probabiliste.
6. **Complément ADAS — Niveau Débutant** : Synthèses et glossaire des technologies d'aide à la conduite.

---

## 🚀 Installation & Démarrage Rapide

### 1. Cloner le Dépôt & Installer les Dépendances

```powershell
# Cloner le projet
git clone https://github.com/FaresAyedi45/adas_agent.git
cd adas_agent

# Créer un environnement virtuel Python (Python 3.10 recommandé)
python -m venv venv

# Activer l'environnement
# Sur Windows :
.\venv\Scripts\activate
# Sur Linux/macOS :
# source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configurer la Clé API

Créez un fichier `.env` à la racine en copiant l'exemple :

```powershell
copy .env.example .env
```

Puis ouvrez `.env` et renseignez votre clé Groq gratuite :
```ini
GROQ_API_KEY=gsk_votre_cle_groq_ici
```

*(Vous pouvez obtenir une clé gratuite en 30 secondes sur [console.groq.com](https://console.groq.com/keys)).*

### 3. Construire la Base Vectorielle (Une seule fois)

```powershell
python scripts\build_vectordb.py
```
*Cette commande découpe et vectorise les documents PDF dans le dossier `chroma_db/`.*

### 4. Lancer l'Application

```powershell
streamlit run agent_app.py --server.port 8502
```

Ouvrez ensuite votre navigateur sur **http://localhost:8502**.

---

## 🧪 Scénarios de Test pour la Démonstration

Voici 4 questions types illustrant toutes les capacités de l'agent :

### Test 1 : Définition & Vulgarisation (Détection automatique : 🎓 Étudiant)
> **Question :** *"C'est quoi l'ACC et comment ça marche ?"*  
> **Comportement attendu :** L'agent détecte le profil Étudiant, explique le régulateur de vitesse adaptatif avec des analogies claires et cite les pages d'introduction.

### Test 2 : Norme & Analyse Système (Détection automatique : 👷 Ingénieur)
> **Question :** *"Quel est le niveau ASIL requis pour un système AEB selon l'ISO 26262 et pourquoi ?"*  
> **Comportement attendu :** L'agent cite l'analyse HARA, le croisement S3 + E4 + C3 menant à l'ASIL D, la redondance matérielle (Lockstep) et cite précisément le *Manuel d'Expertise ADAS*.

### Test 3 : Continuité Contextuelle & Mémoire
> **Question précédente :** *"Quels sont les avantages de l'ADAS ?"*  
> **Question de suivi :** *"Et quelle formule cinématique permet de déclencher ce freinage d'urgence ?"*  
> **Comportement attendu :** L'agent relie *"ce freinage d'urgence"* à l'AEB mentionné précédemment grâce à la mémoire de session. Si la formule exacte n'est pas dans le corpus, il indique en toute transparence la limite de sa base documentaire.

### Test 4 : Examen des Limites et Anti-Hallucination
> **Question :** *"Donne-moi le code source en C du driver LiDAR Velodyne."*  
> **Comportement attendu :** L'agent signale que le code source n'est pas présent dans le corpus documentaire de référence et refuse d'inventer des éléments non vérifiés.

---

## 📁 Structure du Projet

```
adas_agent/
├── agent_app.py              # Interface utilisateur Streamlit (Cockpit HUD)
├── agent_core.py             # Moteur du cycle ReAct, scoring de confiance, détection de rôle
├── prompt_manager.py         # Gouvernance des 3 personas et injection du contexte
├── memory_manager.py         # Gestion de la mémoire conversationnelle (fenêtre glissante)
├── rag_engine.py             # Moteur RAG ChromaDB avec expansion d'acronymes ADAS
├── requirements.txt          # Dépendances Python du projet
├── .env.example              # Modèle de configuration pour la clé API Groq
├── .gitignore                # Fichiers exclus du suivi Git (venv, base vectorielle, cache)
├── data/
│   └── pdfs/                 # Documents techniques et normatifs ADAS de référence
└── scripts/
    ├── build_vectordb.py     # Script d'indexation vectorielle des PDFs
    └── validate_agent.py     # Suite de tests automatisés (16 tests de validation)
```

---

## ⚙️ Suite de Validation Automatisée

Pour vérifier l'intégrité de tous les composants de l'agent :

```powershell
python scripts\validate_agent.py
```

*Résultat attendu : **16/16 PASS** (Base documentaire, Personas, Classification d'intentions, RAG, Mémoire glissante, Scores de confiance).*

---

## 🛠️ Technologies Utilisées

- **Langage :** Python 3.10
- **Interface UI :** Streamlit (Design Cockpit HUD automobile)
- **Modèle de Langage (LLM) :** LLaMA-3 / GPT-OSS via API Groq ultra-rapide
- **Orchestration RAG :** LangChain
- **Base Vectorielle :** ChromaDB (embeddings `sentence-transformers/all-MiniLM-L6-v2`)
- **Mémoire & Raisonnement :** Architecture ReAct native avec persistance d'état JSON

---

## 👥 Auteurs

- **Selim Ghouaiel**
- **Fares Ayedi**
