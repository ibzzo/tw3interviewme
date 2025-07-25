# Test Technique - Ingénieur IA Générative

Ce projet contient les implémentations pour le test technique d'ingénieur IA générative, divisé en trois parties principales.

## 📁 Structure du Projet

```
entretient/
├── chatbot-ia-generative/    # Partie 1 & 2 : Chatbot avec recherche web
├── vlm_project/              # Partie 3 : Démo VLM avec Qwen2.5-VL
└── README.md                 # Ce fichier
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

### Installation Complète
```bash
# 1. Cloner le projet
git clone https://github.com/ibzzo/tw3interviewme.git
cd entretient

# 2. Installer le chatbot
cd chatbot-ia-generative
pip install -r requirements.txt
npm install --prefix frontend

# 3. Installer le VLM (optionnel)
cd ../vlm_project
python -m venv venv_vlm
source venv_vlm/bin/activate
pip install -r requirements.txt
```

## 📝 Configuration

Créer un fichier `.env` dans `chatbot-ia-generative/` :
```env
OPENROUTER_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here
```

## 🚀 Lancement

### Chatbot (Mode Cloud uniquement)
```bash
cd chatbot-ia-generative
# Backend Django
python manage.py runserver

# Dans un autre terminal - Frontend
cd frontend
npm start
```

### Chatbot (Avec vLLM local)
```bash
cd chatbot-ia-generative
# Terminal 1 - vLLM
source venv_vllm/bin/activate
export VLLM_CPU_KVCACHE_SPACE=8
vllm serve "microsoft/Phi-3-mini-4k-instruct" --host 0.0.0.0 --port 8080

# Terminal 2 - Backend Django
source venv/bin/activate
python manage.py runserver

# Terminal 3 - Frontend
cd frontend
npm start
```

→ Frontend : http://localhost:3000
→ Backend : http://localhost:8000
→ vLLM : http://localhost:8080

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