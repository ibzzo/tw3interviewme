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
- Génération de réponses avec OpenRouter (Qwen-2.5-32B)
- Citations inline des sources [1], [2] comme Claude
- Interface React moderne et épurée

[→ Voir les détails d'installation et d'utilisation](./chatbot-ia-generative/README.md)

### Partie 3 : Vision Language Model (VLM)
Démonstration d'un modèle VLM local utilisant Qwen2.5-VL-3B.

**Fonctionnalités :**
- Analyse d'images locales avec vLLM
- Réponses aux questions sur le contenu visuel
- Optimisé pour Mac Apple Silicon

[→ Voir les détails et l'analyse théorique](./vlm_project/README.md)

## 🛠 Installation Rapide

### Prérequis
- Python 3.12 (pour vLLM)
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

### Chatbot
```bash
cd chatbot-ia-generative
./start.sh
```
→ Frontend : http://localhost:3000
→ Backend : http://localhost:8000

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