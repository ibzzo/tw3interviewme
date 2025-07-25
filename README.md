# Test Technique - Ingénieur IA Générative

Ce projet contient les implémentations pour le test technique d'ingénieur IA générative, divisé en trois parties principales.

## 📁 Structure du Projet

```
tw3interviewme/
├── venv_vllm/               # 🐍 Python 3.12 pour vLLM (partagé)
├── chatbot-ia-generative/    # Partie 1 & 2 : Chatbot avec recherche web
│   ├── venv/                # 🐍 Python 3.12 pour Django
│   └── frontend/           # ⚛️ React TypeScript
├── vlm_project/             # Partie 3 : Démo VLM
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
- Python 3.12 (pour Django ET vLLM)
- Node.js 16+
- 8GB+ de RAM

### ⚠️ Notes importantes
- **Utilisez Python 3.12** (Python 3.13 cause des problèmes de compatibilité)
- **Version vLLM** : Utilisez vLLM 0.9.2 (version testée et fonctionnelle sur macOS)

### Installation Complète

#### 1. Cloner le projet
```bash
git clone https://github.com/ibzzo/tw3interviewme.git
cd tw3interviewme
```

#### 2. Installer vLLM (partagé pour chatbot et VLM)
```bash
# Créer l'environnement vLLM à la racine
python3.12 -m venv venv_vllm
source venv_vllm/bin/activate
pip install -r requirements_vllm.txt
deactivate
```

#### 3. Chatbot IA (Backend + Frontend)
```bash
cd chatbot-ia-generative

# Créer l'environnement Django
python3.12 -m venv venv
source venv/bin/activate

# Installer Django et dépendances
pip install -r requirements.txt

# Configurer la base de données
python manage.py migrate

# Installer le frontend
cd frontend
npm install
cd ..
```

## 📝 Configuration

Créer un fichier `.env` dans `chatbot-ia-generative/` :
```bash
cd chatbot-ia-generative
touch .env
# Éditer .env et ajouter vos clés API
```

Contenu du `.env` :
```env
OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
SERPAPI_API_KEY=votre-cle-serpapi-ici
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

# Terminal 1 - vLLM
cd .. # Retour à la racine tw3interviewme
source venv_vllm/bin/activate
export VLLM_CPU_KVCACHE_SPACE=8
vllm serve "microsoft/Phi-3-mini-4k-instruct" --host 0.0.0.0 --port 8080

# Terminal 2 - Backend Django (nouveau terminal)
cd chatbot-ia-generative
source venv/bin/activate
python manage.py runserver

# Terminal 3 - Frontend React
cd chatbot-ia-generative/frontend
npm start
```

### Accès
- 🌐 **Frontend** : http://localhost:3000
- 🔧 **Backend API** : http://localhost:8000
- 🤖 **vLLM** : http://localhost:8080 (si activé)


### VLM Demo
```bash
# Terminal 1 - vLLM pour VLM
source venv_vllm/bin/activate
cd vlm_project
./start_vllm.sh

# Terminal 2 - Script demo
source venv_vllm/bin/activate
cd vlm_project

# Copier d'abord une image test
cp ~/Desktop/votre_image.jpg ./test_image.jpg

# Lancer l'analyse
python vlm_demo.py test_image.jpg
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
Ibrahima DIAO

## 📄 License
Ce projet est développé dans le cadre d'un test technique.