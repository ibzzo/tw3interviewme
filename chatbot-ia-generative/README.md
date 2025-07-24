# Chatbot IA avec Recherche Web Intégrée

[← Retour au projet principal](../README.md)

Implémentation des parties 1 & 2 du test technique : un chatbot intelligent qui combine recherche web en temps réel et génération de réponses contextuelles.

## ✨ Fonctionnalités Principales

- **Recherche Web Intelligente** : Le LLM génère d'abord une requête optimisée, puis effectue une recherche multi-sources
- **Génération Contextuelle** : Utilise exclusivement les résultats de recherche pour générer des réponses précises
- **Citations Inline** : Système de citations [1], [2] cliquables comme Claude Search
- **Interface Épurée** : Design minimaliste inspiré de Claude
- **Multi-sources** : SerpAPI, DuckDuckGo, Tavily, Searx, etc.

## 🏗 Architecture Technique

```
chatbot-ia-generative/
├── chat/                      # Application Django
│   ├── models.py             # Modèles de données
│   ├── views.py              # API endpoints
│   ├── services/             # Services métier
│   │   ├── openrouter_optimized.py
│   │   └── intelligent_search.py
├── chatbot_backend/          # Configuration Django
├── frontend/                 # React + TypeScript
│   └── src/components/       # Composants UI
└── manage.py                # Point d'entrée Django
```

## 📋 Prérequis

- Python 3.8+
- Node.js 16+
- Clés API : OpenRouter et SerpAPI

## 🛠 Installation Détaillée

### 1. Backend Django

```bash
# Depuis le dossier chatbot-ia-generative
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos clés API

# Base de données
python manage.py migrate

# Lancer le serveur
python manage.py runserver
```

### 2. Frontend React

```bash
cd frontend
npm install
npm start
```

## ⚙️ Configuration

Créer `.env` à la racine du projet :

```env
# OpenRouter
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen-2.5-32b-instruct:free

# Search APIs
SERPAPI_API_KEY=your_serpapi_key
DUCKDUCKGO_ENABLED=True
TAVILY_API_KEY=optional_key
```

## 🚀 Utilisation

1. Accédez à http://localhost:3000
2. Posez votre question dans le chat
3. Le système :
   - Analysera si une recherche est nécessaire
   - Générera une requête optimisée
   - Effectuera la recherche sur plusieurs sources
   - Générera une réponse avec citations [1], [2] cliquables

### Exemple de requête :
```
"Quels sont les derniers développements en IA générative cette semaine ?"
```

## 📡 API Endpoints

### POST /api/v1/chat/
Endpoint principal du chatbot

**Request:**
```json
{
  "message": "Votre question ici",
  "conversation_id": "optional_id"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": {
    "role": "assistant",
    "content": "Réponse avec citations [1], [2]",
    "sources": [
      {
        "title": "Titre de la source",
        "url": "https://...",
        "snippet": "Extrait pertinent"
      }
    ]
  }
}
```

## 📁 Structure Détaillée

### Services Backend

- **`openrouter_optimized.py`** : Gestion des appels LLM avec contexte forcé
- **`intelligent_search.py`** : Orchestration des recherches multi-sources
- **`multi_search.py`** : Agrégation et déduplication des résultats

### Composants Frontend

- **`ChatInterface.tsx`** : Container principal
- **`MessageList.tsx`** : Affichage des messages avec citations inline
- **`MessageInput.tsx`** : Zone de saisie minimaliste

## 🔧 Optimisations

1. **Cache de recherche** : Évite les recherches répétées
2. **Déduplication** : Supprime les résultats en double
3. **Citations intelligentes** : Transformation automatique [Source: ...] → [1]
4. **Nettoyage des réponses** : Suppression des sections "Sources consultées"

## 🚀 Déploiement

Voir le [README principal](../README.md) pour les options de déploiement cloud.

## 📝 Notes Techniques

- Le modèle Qwen-2.5-32B est utilisé via OpenRouter (gratuit)
- Les recherches sont limitées aux sources configurées
- Le système force l'utilisation du contexte de recherche
- Interface responsive et accessible

---

Pour la partie VLM et l'analyse théorique, voir [vlm_project](../vlm_project/README.md)