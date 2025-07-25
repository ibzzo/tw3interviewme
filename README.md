# Test Technique - Ingénieur IA Générative

Ce projet contient les implémentations pour le test technique d'ingénieur IA générative, divisé en trois parties principales.

## 📁 Structure du Projet

```
tw3interviewme/
├── chatbot-ia-generative/    # Partie 1 & 2 : Chatbot avec recherche web
│   ├── venv/                # 🐍 Python 3.13 pour Django
│   ├── venv_vllm/          # 🐍 Python 3.12 pour vLLM
│   └── frontend/           # ⚛️ React TypeScript
├── vlm_project/             # Partie 3 : Démo VLM avec Qwen2.5-VL
│   └── venv_vlm_demo/      # 🐍 Python 3.12 pour VLM demo
└── README.md               # Ce fichier
```

## 🚀 Parties du Test

### Partie 1 & 2 : Chatbot IA avec Recherche Web
Un chatbot intelligent qui combine recherche web en temps réel et génération de réponses contextuelles.

**Fonctionnalités principales :**
- Recherche web intelligente multi-sources
- Double mode LLM : vLLM local (Phi-3) ou OpenRouter cloud (Qwen-2.5-32B)
- Panneau de sources interactif
- Sélecteur de modèle en temps réel
- Interface React moderne et épurée

**⚠️ Important : Les réponses aux questions théoriques (3.1, 3.2, 4) sont incluses dans le README du chatbot.**

[→ Voir les détails d'installation et d'utilisation](./chatbot-ia-generative/README.md)

### Partie 3 : Vision Language Model (VLM)
Démonstration d'un modèle VLM local utilisant Qwen2.5-VL-3B.

**Fonctionnalités :**
- Analyse d'images locales avec vLLM
- Réponses aux questions sur le contenu visuel
- Optimisé pour Mac Apple Silicon

[→ Voir les détails et l'analyse théorique](./vlm_project/README.md)

## 📚 Réponses aux Questions Théoriques

Les réponses complètes aux questions du test sont disponibles :
- **Question 3.1** (Architecture Azure) : Dans [chatbot-ia-generative/README.md](./chatbot-ia-generative/README.md#31-architecture-et-déploiement-azure)
- **Question 3.2** (Optimisation performances) : Dans [chatbot-ia-generative/README.md](./chatbot-ia-generative/README.md#question-32--amélioration-de-la-vitesse-de-traitement)
- **Question 4** (Architecture VLM) : Dans [chatbot-ia-generative/README.md](./chatbot-ia-generative/README.md#question-4--architecture-vlm-vision-language-model)

## 🛠 Installation Rapide

### Prérequis
- Python 3.13 (Django) + Python 3.12 (vLLM)
- Node.js 16+
- 8GB+ de RAM

### Installation Complète (3 environnements)

#### 1. Cloner le projet
```bash
git clone https://github.com/ibzzo/tw3interviewme.git
cd tw3interviewme
```

#### 2. Backend Django (Python 3.13)
```bash
cd chatbot-ia-generative

# Créer l'environnement virtuel Python 3.13
python3.13 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
python manage.py migrate
```

#### 3. vLLM Local (Python 3.12) - Optionnel
```bash
# IMPORTANT: Rester dans le dossier chatbot-ia-generative

# Créer un 2ème environnement virtuel avec Python 3.12
python3.12 -m venv venv_vllm
source venv_vllm/bin/activate  # Linux/Mac
# ou: venv_vllm\Scripts\activate  # Windows

# Installer vLLM (cela installe automatiquement torch, transformers, etc.)
pip install vllm

# Désactiver pour revenir à l'env principal
deactivate
```

#### 4. Frontend React
```bash
# Retourner dans l'environnement principal
source venv/bin/activate

# Installer les dépendances frontend
cd frontend
npm install
cd ..
```

#### 5. VLM Demo (3ème environnement) - Optionnel
```bash
cd ../vlm_project

# Créer un 3ème environnement virtuel
python3.12 -m venv venv_vlm_demo
source venv_vlm_demo/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 📝 Configuration

Créer un fichier `.env` dans `chatbot-ia-generative/` :
```env
OPENROUTER_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here
```

## 🚀 Lancement

### Mode 1 : Cloud OpenRouter uniquement (2 terminaux)
```bash
cd chatbot-ia-generative

# Terminal 1 - Backend Django
source venv/bin/activate        # ⚠️ Utiliser venv (pas venv_vllm)
python manage.py runserver

# Terminal 2 - Frontend React
cd frontend
npm start
```

### Mode 2 : Avec vLLM local (3 terminaux)
```bash
cd chatbot-ia-generative

# Terminal 1 - vLLM (Python 3.12)
source venv_vllm/bin/activate   # ⚠️ Utiliser venv_vllm (pas venv)
export VLLM_CPU_KVCACHE_SPACE=8
vllm serve "microsoft/Phi-3-mini-4k-instruct" --host 0.0.0.0 --port 8080 --device cpu

# Terminal 2 - Backend Django (Python 3.13)
source venv/bin/activate        # ⚠️ Utiliser venv (pas venv_vllm)
python manage.py runserver

# Terminal 3 - Frontend React
cd frontend
npm start
```

### Accès
- 🌐 **Frontend** : http://localhost:3000
- 🔧 **Backend API** : http://localhost:8000
- 🤖 **vLLM** : http://localhost:8080 (si activé)

### VLM Demo
```bash
cd vlm_project
./start_vllm.sh        # Terminal 1
python vlm_demo.py     # Terminal 2
```

## 📚 Documentation
- [Chatbot - Documentation complète](./chatbot-ia-generative/README.md)
- [VLM - Analyse théorique et pratique](./vlm_project/README.md)

## 🏗 Architecture

### Chatbot
- **Backend** : Django REST Framework + OpenRouter API
- **Frontend** : React + TypeScript + Styled Components
- **Recherche** : Multi-sources (SerpAPI, DuckDuckGo, Tavily)

### VLM
- **Modèle** : Qwen2.5-VL-3B-Instruct
- **Serveur** : vLLM optimisé pour CPU
- **Interface** : Script Python interactif

## 👤 Auteur
Ibrahim Adiao

## 📄 License
Ce projet est développé dans le cadre d'un test technique.