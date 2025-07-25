# Chatbot IA avec Recherche Web et LLM Local/Cloud

## 📋 Description du projet

Chatbot intelligent développé pour le test technique d'Ingénieur IA Générative. Le système combine :
- **Recherche web intelligente** avec intégration de multiples sources
- **Double mode LLM** : Local (vLLM) ou Cloud (OpenRouter)
- **Interface moderne** avec panneau de sources et sélecteur de modèle

## ✨ Fonctionnalités implémentées

### Partie 1 : Chatbot avec accès Internet
- ✅ Recherche web multi-sources (SerpAPI, fallbacks)
- ✅ Intégration LLM (OpenRouter avec Qwen-2.5-32b gratuit)
- ✅ Interface React moderne et responsive
- ✅ Gestion des erreurs et limites de taux
- ✅ **Bonus** : LLM local avec vLLM (Phi-3)

### Fonctionnalités avancées
- 🎯 **Sélecteur de modèle** : Bascule facile entre local/cloud
- 📚 **Panneau de sources** : Affichage élégant des références
- 🔍 **Recherche intelligente** : Optimisation automatique des requêtes
- ⚡ **Cache intelligent** : Performance optimisée

## 🛠️ Installation

### Prérequis
- Python 3.13 (Django) + Python 3.12 (vLLM)
- Node.js 14+
- macOS/Linux recommandé

### 1. Backend Django (Python 3.13)
```bash
cd chatbot-ia-generative
python3.13 -m venv venv
source venv/bin/activate

# Installer : Django, DRF, requests, python-dotenv, django-cors-headers
pip install -r requirements.txt

# Configuration
cp .env.example .env  # Ajouter votre clé OpenRouter

# Base de données
python manage.py migrate
```

### 2. vLLM (optionnel pour mode local)

#### Installation (Python 3.12 requis)
```bash
python3.12 -m venv venv_vllm
source venv_vllm/bin/activate

# Installer uniquement vLLM (inclut torch, transformers automatiquement)
pip install vllm
```

#### Configuration et lancement
```bash
# Activer l'environnement
source venv_vllm/bin/activate

# Configurer pour CPU
export VLLM_CPU_KVCACHE_SPACE=8

# Lancer le serveur vLLM
vllm serve "microsoft/Phi-3-mini-4k-instruct" \
    --host 0.0.0.0 \
    --port 8080 \
    --device cpu
```

#### Modèles recommandés
- **microsoft/Phi-3-mini-4k-instruct** (3.8B) - Recommandé, bon équilibre
- **microsoft/phi-2** (2.7B) - Plus rapide sur CPU
- **google/gemma-2b** (2B) - Ultra léger

#### Résolution des problèmes
- **Port déjà utilisé** : Changer avec `--port 8081`
- **Mémoire insuffisante** : Réduire avec `--max-model-len 2048`
- **Module non trouvé** : Vérifier `which python` pointe vers venv_vllm

### 3. Frontend React
```bash
cd frontend
npm install
```

## 🚀 Lancement

### Mode 1 : Cloud uniquement (2 terminaux)
```bash
# Terminal 1 - Backend Django
source venv/bin/activate        # ⚠️ venv (pas venv_vllm)
python manage.py runserver

# Terminal 2 - Frontend React
cd frontend && npm start
```

### Mode 2 : Avec vLLM local (3 terminaux)
```bash
# Terminal 1 - vLLM
source venv_vllm/bin/activate   # ⚠️ venv_vllm (pas venv)
export VLLM_CPU_KVCACHE_SPACE=8
vllm serve "microsoft/Phi-3-mini-4k-instruct" --host 0.0.0.0 --port 8080

# Terminal 2 - Backend Django
source venv/bin/activate        # ⚠️ venv (pas venv_vllm)
python manage.py runserver

# Terminal 3 - Frontend React
cd frontend && npm start
```

Accès : http://localhost:3000

## 📝 Scénario de test

**Question type** : "Quels sont les derniers développements en IA générative annoncés cette semaine ? Donne-moi 3 exemples concrets avec leurs sources."

**Résultat attendu** :
- Détection automatique du besoin de recherche
- Recherche web optimisée avec contrainte temporelle
- Synthèse avec 3 exemples concrets
- Sources affichées dans le panneau latéral

---

# Partie 2 : Questions théoriques

## 3.1 Architecture et Déploiement Azure

### Plan de déploiement étape par étape

#### 1. Prérequis Azure
- **Souscription Azure** active
- **Permissions nécessaires** :
  - Contributeur sur la souscription
  - Administrateur Azure AD (pour les identités managées)
  - Contributeur Key Vault
- **Outils** : Azure CLI, Docker, kubectl

#### 2. Architecture cible sur Azure

```
┌─────────────────────┐
│   Azure Front Door  │ ← CDN + WAF + Load Balancer
└──────────┬──────────┘
           │
┌──────────▼──────────┐     ┌─────────────────┐
│  App Service Plan   │────▶│   Azure Cache   │
│  - Frontend (React) │     │   for Redis     │
│  - Backend (Django) │     └─────────────────┘
└──────────┬──────────┘              │
           │                         │
┌──────────▼──────────┐     ┌───────▼─────────┐
│ Azure Container     │     │   Key Vault     │
│ Instance (vLLM)     │     │  (API Keys)     │
│ avec GPU (optionnel)│     └─────────────────┘
└─────────────────────┘
           │
┌──────────▼──────────┐
│  Azure Database     │
│  for PostgreSQL     │
└─────────────────────┘
```

#### 3. Services Azure requis

| Service | Utilisation | SKU recommandé |
|---------|-------------|----------------|
| App Service | Frontend + Backend | P1v3 (Production) |
| PostgreSQL | Base de données | Basic 2vCore |
| Redis Cache | Cache + Sessions | Basic C1 |
| Key Vault | Secrets | Standard |
| Container Instance | vLLM (optionnel) | GPU NC6 |
| Front Door | CDN + Sécurité | Standard |
| Application Insights | Monitoring | Pay-as-you-go |

#### 4. Estimation des coûts mensuels

| Service | Configuration | Coût estimé |
|---------|--------------|-------------|
| App Service (P1v3) | 2 instances | 180€ |
| PostgreSQL | Basic 2vCore | 50€ |
| Redis | Basic C1 | 40€ |
| Front Door | Standard | 35€ |
| Key Vault | Standard | 5€ |
| Application Insights | 5GB/mois | 25€ |
| **Sans GPU** | | **~335€/mois** |
| Container Instance GPU | NC6 (optionnel) | +500€ |
| **Avec GPU** | | **~835€/mois** |

#### 5. Déploiement pas à pas

```bash
# 1. Connexion et création du groupe
az login
az group create --name rg-chatbot-prod --location westeurope

# 2. Key Vault pour les secrets
az keyvault create \
  --name kv-chatbot-unique \
  --resource-group rg-chatbot-prod \
  --location westeurope

# Ajouter les secrets
az keyvault secret set \
  --vault-name kv-chatbot-unique \
  --name "openrouter-api-key" \
  --value "YOUR_KEY"

# 3. PostgreSQL
az postgres flexible-server create \
  --resource-group rg-chatbot-prod \
  --name chatbot-db-prod \
  --location westeurope \
  --tier Burstable \
  --sku-name B_Standard_B1ms \
  --storage-size 32 \
  --version 15

# 4. Redis Cache
az redis create \
  --location westeurope \
  --name chatbot-redis \
  --resource-group rg-chatbot-prod \
  --sku Basic \
  --vm-size c1

# 5. App Service Plan
az appservice plan create \
  --name asp-chatbot \
  --resource-group rg-chatbot-prod \
  --location westeurope \
  --sku P1v3 \
  --is-linux

# 6. Web Apps
az webapp create \
  --resource-group rg-chatbot-prod \
  --plan asp-chatbot \
  --name chatbot-backend-prod \
  --runtime "PYTHON:3.11"

az webapp create \
  --resource-group rg-chatbot-prod \
  --plan asp-chatbot \
  --name chatbot-frontend-prod \
  --runtime "NODE:18-lts"

# 7. Front Door
az network front-door create \
  --resource-group rg-chatbot-prod \
  --name fd-chatbot \
  --backend-address chatbot-frontend-prod.azurewebsites.net
```

#### 6. Points d'attention critiques

**Accès et permissions** :
- ✅ Utiliser les Managed Identities pour l'accès aux services
- ✅ RBAC pour limiter les accès par rôle
- ✅ Network Security Groups pour isoler les composants

**Sécurité des secrets** :
- ✅ Toutes les clés API dans Key Vault
- ✅ Rotation automatique des secrets
- ✅ Audit logs activés

**Prérequis techniques** :
- Domaine custom pour Front Door
- Certificats SSL (géré par Azure)
- Firewall rules pour PostgreSQL

#### 7. CI/CD Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: ['main']

stages:
- stage: Build
  jobs:
  - job: BuildBackend
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: Docker@2
      inputs:
        command: 'buildAndPush'
        repository: 'chatbot-backend'
        dockerfile: 'Dockerfile'
        
  - job: BuildFrontend
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: '18.x'
    - script: |
        cd frontend
        npm install
        npm run build
        
- stage: Deploy
  jobs:
  - deployment: DeployProd
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              appType: 'webAppLinux'
              appName: 'chatbot-backend-prod'
```

#### 8. Monitoring et logs

- **Application Insights** : Intégré dans le code Django/React
- **Log Analytics** : Centralisation des logs
- **Alertes** : CPU > 80%, Erreurs > 10/min
- **Dashboards** : Métriques temps réel

### Stratégie de backup

1. **PostgreSQL** : Backup automatique quotidien (rétention 7 jours)
2. **Code** : Git + Azure Repos
3. **Configurations** : Infrastructure as Code (Terraform/ARM)

---

## Architecture simplifiée

```
chatbot-ia-generative/
├── chat/                       # Backend Django
│   ├── services/              # Services essentiels uniquement
│   │   ├── vllm_service.py   # LLM local (Phi-3)
│   │   ├── openrouter_optimized.py   # LLM cloud (Qwen)
│   │   ├── intelligent_search.py     # Recherche web intelligente
│   │   ├── serpapi_service.py        # API de recherche principale
│   │   └── multi_search.py           # Fallback de recherche
│   ├── views.py              # Endpoints API (/chat, /set-model)
│   └── models.py             # Base de données (Conversation, Message)
├── frontend/                  # Interface React
│   └── src/components/       # Composants UI
├── venv/                     # Python 3.13 pour Django
├── venv_vllm/               # Python 3.12 pour vLLM
└── requirements.txt         # Dépendances Django
```

## 🔐 Variables d'environnement

```env
# Backend
OPENROUTER_API_KEY=sk-or-v1-xxxxx
SERPAPI_API_KEY=xxxxx
VLLM_BASE_URL=http://localhost:8080
VLLM_MODEL=microsoft/Phi-3-mini-4k-instruct

# Redis (production)
REDIS_HOST=chatbot-redis.redis.cache.windows.net
REDIS_KEY=xxxxx

# Database (production)
DATABASE_URL=postgresql://user:pass@server/db
```

## ⚠️ Limites et quotas

- **OpenRouter (gratuit)** : ~10 requêtes/minute, 200/jour
- **SerpAPI (gratuit)** : 100 recherches/mois
- **Solution** : Utiliser vLLM local quand limite atteinte

## 📊 Performances

- **OpenRouter Cloud** : 2-5s par réponse
- **vLLM Local (CPU)** : 30s-2min par réponse ⚠️
- **vLLM Local (GPU)** : 2-10s par réponse
- **Recherche web** : <2s avec cache

## 🤝 Points forts de l'implémentation

1. **Architecture modulaire** : Services découplés et réutilisables
2. **Double mode LLM** : Flexibilité local/cloud
3. **UX moderne** : Interface intuitive avec feedback temps réel
4. **Production-ready** : Gestion d'erreurs, logs, monitoring
5. **Sécurité** : Secrets externalisés, CORS configuré

---

# Partie 3 : Questions théoriques complémentaires

## Question 3.2 : Amélioration de la vitesse de traitement

### Stratégies d'optimisation pour réduire la latence

#### 1. Optimisation du modèle
- **Quantization** : Réduction INT8/INT4 (↓75% mémoire, ↑2-4x vitesse)
- **Model pruning** : Suppression des poids non essentiels
- **Knowledge distillation** : Modèle plus petit entraîné sur le grand

#### 2. Architecture optimisée
```
Client → Load Balancer → API Gateway
              ↓                ↓
      Fast Router (Phi-2)  vLLM Cluster (Phi-3)
              ↓                ↓
          Cache Layer (Redis + Vector DB)
```

#### 3. Techniques d'accélération
- **Streaming des réponses** : L'utilisateur voit la réponse se construire
- **Batching dynamique** : Traitement groupé des requêtes
- **Cache sémantique** : Réutilisation des réponses similaires
- **Préfixe caching vLLM** : `--enable-prefix-caching`

#### 4. Métriques attendues
| Optimisation | Gain de performance |
|--------------|-------------------|
| Quantization 4-bit | 4x plus rapide |
| Streaming | Perception 50% plus rapide |
| Cache intelligent | 80% hit rate |
| **Total** | **5-15s → 1-3s** |

---

## Question 4 : Architecture VLM (Vision-Language Model)

### Intégration d'un modèle de vision dans le chatbot

#### 1. Architecture proposée
```python
# services/vlm_service.py
class VLMService:
    def __init__(self):
        self.model = "llava-hf/llava-1.5-7b-hf"
        self.processor = AutoProcessor.from_pretrained(self.model)
        
    async def analyze_image(self, image_path: str, prompt: str):
        image = Image.open(image_path)
        inputs = self.processor(text=prompt, images=image, return_tensors="pt")
        
        output = self.model.generate(**inputs, max_new_tokens=500)
        return self.processor.decode(output[0], skip_special_tokens=True)
```

#### 2. Endpoint Django
```python
class ImageAnalysisView(APIView):
    parser_classes = (MultiPartParser,)
    
    async def post(self, request):
        image_file = request.FILES.get('image')
        prompt = request.data.get('prompt', 'Describe this image')
        
        # Analyse avec VLM
        vlm_service = VLMService()
        result = await vlm_service.analyze_image(temp_path, prompt)
        
        return Response({'analysis': result})
```

#### 3. Frontend avec upload
```typescript
const ImageUploader: React.FC = () => {
    const [preview, setPreview] = useState<string | null>(null);
    
    const handleUpload = async (file: File) => {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await axios.post('/api/v1/analyze-image/', formData);
        setAnalysis(response.data.analysis);
    };
}
```

#### 4. Modèles VLM recommandés
| Modèle | Taille | Use Case |
|--------|--------|----------|
| CLIP | 400M | Classification rapide |
| BLIP-2 | 3B | Génération de légendes |
| LLaVA-1.5 | 7B | Analyse détaillée |
| CogVLM | 17B | Questions complexes |

#### 5. Optimisations spécifiques
- **Prétraitement** : Redimensionnement intelligent des images
- **Cache** : Hash d'image pour éviter retraitement
- **Batching** : Traitement groupé des images
- **Quantization** : Modèles 4-bit pour performance

### Défis et solutions
1. **Latence** → Modèle quantizé + streaming
2. **Mémoire GPU** → Offloading CPU dynamique
3. **Scalabilité** → Queue Celery + workers GPU