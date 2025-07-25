# Vision Language Model (VLM) - Qwen2.5-VL

[← Retour au projet principal](../README.md)

Implémentation de la partie 3 du test technique : démonstration d'un VLM local avec Qwen2.5-VL-3B.

## 🎯 Objectif

Créer un script Python utilisant un Vision Language Model local pour :
- Analyser des images locales
- Extraire du texte (OCR)
- Répondre à des questions sur le contenu visuel

## 🚀 Installation

### Prérequis
- Mac Apple Silicon (testé sur M4)
- Python 3.12 (⚠️ vLLM ne supporte pas Python 3.13)
- 8GB+ de RAM disponible

### Installation

L'environnement vLLM est partagé avec le chatbot. Voir l'installation complète dans le [README principal](../README.md).

## 💻 Utilisation

### Étape 1 : Démarrer le serveur vLLM

```bash
# Depuis la racine du projet
source venv_vllm/bin/activate
cd vlm_project
./start_vllm.sh
```

Le serveur démarre sur http://localhost:8000. Attendez le message "Uvicorn running" avant de continuer.

### Étape 2 : Préparer une image test

```bash
# Copier une image de votre choix dans le dossier vlm_project
# Par exemple :
cp ~/Desktop/mon_image.jpg ./test_image.jpg

# Ou télécharger une image d'exemple :
curl -o test_image.jpg https://images.unsplash.com/photo-1574158622682-e40e69881006
```

### Étape 3 : Exécuter le script VLM

Dans un nouveau terminal :

```bash
# Depuis la racine du projet
source venv_vllm/bin/activate
cd vlm_project

# Analyse basique d'image (remplacer test_image.jpg par votre nom de fichier)
python vlm_demo.py test_image.jpg

# Avec prompt personnalisé
python vlm_demo.py test_image.jpg "Extract all text from this document"

# Avec URL d'image
python vlm_demo.py https://example.com/image.jpg
```

## 📁 Fichiers du projet

- **`vlm_demo.py`** : Script principal avec animation de chargement
- **`start_vllm.sh`** : Script optimisé pour démarrer vLLM sur CPU
- **`README.md`** : Documentation et analyse théorique

## ⚡ Optimisations appliquées

1. **Configuration CPU** : `VLLM_CPU_KVCACHE_SPACE=8` pour Mac
2. **Modèle réduit** : `max-model-len=8192` pour économiser la RAM
3. **Timeout ajusté** : 300s pour traitement CPU
4. **Animation visuelle** : Feedback durant le traitement

## 🏗️ Question théorique : Architecture VLM-RAG

### Comment intégrer des VLMs dans un système RAG ?

Pour créer un pipeline RAG multimodal efficace, l'architecture doit résoudre trois défis : extraction intelligente, préservation des relations contextuelles, et recherche unifiée.

### Architecture proposée

```
Documents → Extracteur → VLM Enrichissement → Vectorisation → Index → Recherche
```

### Composants clés

**1. Extraction intelligente**
- Identifie texte, images et leurs relations spatiales
- Préserve les liens (ex: graphique + légende)
- Utilise LayoutLM pour comprendre la structure

**2. Enrichissement VLM**
- Transforme images en descriptions textuelles
- Analyse le contexte pour interpréter correctement
- Exemple : graphique → "croissance 23% Q3 2024"

**3. Vectorisation hybride**
- Vecteurs textuels : embeddings standards
- Vecteurs visuels : représentations CLIP
- Vecteurs unifiés : fusion cross-modale

**4. Indexation stratégique**
```python
{
  "content": "texte ou description",
  "type": "text|image|unified",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "position": 42,
    "relations": ["fig_1", "para_3"],
    "vlm_confidence": 0.95
  }
}
```

**5. Recherche intelligente**
- Expansion de requête automatique
- Fusion pondérée multi-modale
- Reranking pour pertinence finale

### Optimisations pratiques

1. **Chunking contextuel** : Fenêtre de 200 mots autour des images
2. **Cache perceptuel** : Hash des images pour éviter retraitement
3. **Validation VLM** : Détection d'hallucinations
4. **Pipeline asynchrone** : Traitement parallèle

### Avantages

✅ Compréhension holistique des documents  
✅ Recherche flexible (texte → image)  
✅ Contexte préservé automatiquement  
✅ Architecture scalable et modulaire  

### En production

- VLMs locaux (Qwen2.5-VL) pour volume
- APIs cloud (GPT-4V) pour cas complexes
- Cache aggressive (24h+)
- Monitoring par modalité

Cette approche transforme le RAG en système véritablement multimodal, offrant une recherche naturelle où texte et images sont traités équitablement.

## 📝 Notes techniques

- Premier chargement : ~2-3 minutes
- Consommation RAM : ~6-8GB
- Optimisé pour Apple Silicon (Metal)
- Support images locales et URLs

---

Pour le chatbot avec recherche web, voir [chatbot-ia-generative](../chatbot-ia-generative/README.md)