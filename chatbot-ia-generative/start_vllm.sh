#!/bin/bash

echo "🚀 Démarrage de vLLM"

# Vérifier Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 n'est pas installé!"
    echo "Installez-le avec: brew install python@3.12"
    exit 1
fi

# Créer venv si nécessaire
if [ ! -d "venv_vllm" ]; then
    echo "📦 Création de l'environnement virtuel Python 3.12..."
    python3.12 -m venv venv_vllm
fi

# Activer l'environnement
source venv_vllm/bin/activate

# Installer vLLM si nécessaire
if ! command -v vllm &> /dev/null; then
    echo "📦 Installation de vLLM..."
    pip install vllm
fi

# Configuration pour Mac
export VLLM_CPU_KVCACHE_SPACE=8

# Lancer vLLM
echo "🚀 Lancement de vLLM avec meta-llama/Llama-3.2-3B-Instruct"
vllm serve "microsoft/Phi-3-mini-4k-instruct" \
    --max-model-len 4096 \
    --host 0.0.0.0 \
    --port 8080 \
    --dtype float16