# Partie 3 : Vision Language Model (VLM) - Qwen2.5-VL

## 📋 Description

Ce projet implémente la partie 3 du test technique : un script Python utilisant **Qwen/Qwen2.5-VL-3B-Instruct** en local pour traiter des images.

## 🚀 Installation

### Prérequis
- Mac M4 avec 24GB RAM
- Homebrew installé
- Python 3.12 (vLLM ne supporte pas Python 3.13)

### Installation manuelle

```bash
# 1. Installer Python 3.12
brew install python@3.12

# 2. Créer l'environnement virtuel
python3.12 -m venv venv_vlm
source venv_vlm/bin/activate

# 3. Installer les dépendances
pip install vllm requests pillow
```

## 💻 Utilisation

### 1. Démarrer le serveur vLLM

```bash
# Utiliser le script optimisé
./start_vllm.sh

# OU manuellement
source venv_vlm/bin/activate
export VLLM_CPU_KVCACHE_SPACE=8
vllm serve "Qwen/Qwen2.5-VL-3B-Instruct" --max-model-len 8192
```

### 2. Dans un nouveau terminal, exécuter le script

```bash
source venv_vlm/bin/activate

# Avec une image locale
python vlm_demo.py photo.jpg

# Avec un prompt personnalisé
python vlm_demo.py photo.jpg "Extract all text from this image"

# Avec une URL
python vlm_demo.py https://example.com/image.jpg
```

## 📁 Structure

```
vlm_project/
├── README.md              # Ce fichier
├── vlm_demo.py           # Script principal VLM
├── start_vllm.sh         # Script de démarrage optimisé
└── venv_vlm/             # Environnement virtuel (ignoré par git)
```

## ⚠️ Notes importantes

- **Python 3.13 n'est PAS supporté** par vLLM
- Le premier chargement du modèle peut prendre plusieurs minutes
- Le modèle utilise environ 6-8GB de RAM
- Optimisé pour Mac M4 avec accélération Metal

## 🎯 Fonctionnalités

- ✅ Description détaillée d'images
- ✅ Extraction de texte (OCR)
- ✅ Support images locales et URLs
- ✅ Prompts personnalisables
- ✅ Utilisation de Qwen2.5-VL-3B-Instruct

## 🏗️ Question théorique : Architecture VLM pour système RAG

### Comment architecturer un système de vectorisation de documents intégrant des VLMs ?

Pour créer un pipeline RAG multimodal efficace, l'architecture doit résoudre trois défis majeurs : l'extraction intelligente du contenu, la préservation des relations contextuelles, et la recherche unifiée cross-modale.

### 1. Architecture proposée

Le système s'organise autour de 5 composants principaux interconnectés :

**Extracteur Multimodal** → **Préprocesseur VLM** → **Vectorisation Hybride** → **Stockage Indexé** → **Moteur de Recherche**

### 2. Composants clés et leurs rôles

#### 2.1 Extraction intelligente
L'extracteur doit identifier non seulement le texte et les images, mais surtout leurs relations spatiales et sémantiques. Pour un graphique accompagné d'une légende, le système doit maintenir ce lien tout au long du pipeline. Les outils comme LayoutLM comprennent la structure visuelle des documents pour préserver ces associations.

#### 2.2 Enrichissement par VLM
Les VLMs transforment les images en descriptions textuelles riches. Un graphique financier devient "courbe ascendante montrant une croissance de 23% sur Q3 2024". Le VLM analyse aussi le contexte : une image près d'un paragraphe sur les ventes sera interprétée différemment qu'une près d'un texte technique.

#### 2.3 Vectorisation multi-modale
Trois types de vecteurs sont générés :
- **Vecteurs textuels** : embeddings classiques pour le contenu textuel
- **Vecteurs visuels** : représentations CLIP des images
- **Vecteurs unifiés** : fusion cross-modale pour recherche conceptuelle

Cette approche permet de chercher par texte ("graphique des ventes"), par similarité visuelle, ou par concept abstrait ("tendance positive").

#### 2.4 Indexation stratégique
Le stockage utilise des index séparés par modalité avec métadonnées enrichies :
- Position dans le document
- Relations avec autres éléments
- Descriptions VLM
- Scores de confiance

Cette structure permet des requêtes complexes comme "trouver tous les diagrammes techniques avec leurs explications associées".

#### 2.5 Recherche hybride intelligente
Le moteur combine plusieurs stratégies :
- Expansion de requête pour couvrir les synonymes visuels
- Fusion pondérée des résultats multi-modaux
- Reranking cross-encoder pour pertinence finale
- Diversification MMR pour éviter la redondance

### 3. Optimisations critiques

**Chunking contextuel** : Les segments preservent les liens texte-image dans une fenêtre de proximité (ex: 200 mots avant/après).

**Cache perceptuel** : Évite de retraiter des images similaires en utilisant des hash perceptuels avec seuil de similarité.

**Détection d'hallucinations** : Valide que les descriptions VLM correspondent réellement au contenu visuel pour maintenir la qualité.

**Traitement asynchrone** : Les opérations VLM coûteuses sont distribuées pour maintenir la latence acceptable.

### 4. Avantages de cette approche

1. **Compréhension holistique** : Le système comprend les documents comme un humain, en liant naturellement texte et visuels.

2. **Flexibilité de recherche** : Les utilisateurs peuvent chercher par description textuelle d'images qu'ils n'ont jamais vues.

3. **Précision contextuelle** : Les résultats incluent automatiquement les éléments visuels pertinents avec leur contexte.

4. **Scalabilité** : L'architecture modulaire permet d'optimiser chaque composant indépendamment.

### 5. Considérations pratiques

Pour la production, privilégier :
- VLMs locaux pour le volume (Qwen2.5-VL sur GPU)
- APIs cloud (GPT-4V) uniquement pour cas complexes
- Monitoring de la latence par modalité
- Stratégie de cache aggressive (24h minimum)

Cette architecture transforme le RAG traditionnel en système véritablement multimodal, où texte et images sont traités comme citoyens de première classe, offrant une expérience de recherche naturelle et complète.