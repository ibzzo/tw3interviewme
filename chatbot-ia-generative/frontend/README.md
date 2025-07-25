# Frontend - Chatbot IA

## 🎨 Description

Interface React moderne pour le chatbot IA avec:
- Chat en temps réel avec interface intuitive
- Sélecteur de modèle (vLLM local / OpenRouter cloud)
- Panneau de sources avec animation slide
- Design responsive et moderne

## 🚀 Installation

```bash
# Installer les dépendances
npm install

# Lancer en développement
npm start

# Build production
npm run build
```

## 📁 Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx    # Composant principal du chat
│   │   ├── MessageList.tsx      # Liste des messages
│   │   ├── MessageInput.tsx     # Zone de saisie
│   │   ├── ModelSelector.tsx    # Sélecteur LLM
│   │   └── SourcesPanel.tsx     # Panneau des sources
│   ├── services/
│   │   └── api.ts              # Service API
│   └── App.tsx                 # Application principale
└── package.json
```

## 🔧 Configuration

L'API backend est configurée sur `http://localhost:8000` dans:
- `src/services/api.ts`
- `src/components/ChatInterface.tsx`

## 🎯 Fonctionnalités principales

### 1. Chat Interface
- Messages utilisateur/assistant avec avatars
- Indicateur de chargement animé
- Auto-scroll vers le bas
- Support markdown dans les réponses

### 2. Model Selector
- Bascule entre vLLM (local) et OpenRouter (cloud)
- Vérification du statut en temps réel
- Indicateurs visuels (vert = actif, rouge = inactif)
- Actualisation automatique toutes les 10s

### 3. Sources Panel
- Ouverture automatique quand sources disponibles
- Animation slide fluide
- Cartes cliquables avec snippets
- Badge numéroté pour chaque source

## 🛠️ Technologies

- **React** 18 avec TypeScript
- **styled-components** pour le styling
- **Axios** pour les appels API
- **markdown-to-jsx** pour le rendu markdown

## 📝 Scripts disponibles

- `npm start` : Serveur de développement (port 3000)
- `npm build` : Build de production
- `npm test` : Tests unitaires
- `npm eject` : Éjecter la config (non recommandé)

## 💡 Points techniques

### Performance
- Rendu optimisé avec React.memo
- Lazy loading des composants lourds
- Debounce sur la saisie utilisateur

### UX/UI
- Feedback visuel immédiat
- Animations fluides (300ms transitions)
- Design accessible (ARIA labels)
- Mode sombre compatible

### Sécurité
- Sanitization des entrées utilisateur
- Validation côté client et serveur
- CORS configuré pour localhost:8000

