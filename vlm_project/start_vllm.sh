#!/bin/bash

echo "🚀 Démarrage de vLLM avec configuration optimisée pour Mac M4"

# Activer l'environnement
source venv_vlm/bin/activate

# Augmenter l'espace cache et limiter la longueur max
export VLLM_CPU_KVCACHE_SPACE=8

# Lancer vLLM avec des paramètres optimisés
vllm serve "Qwen/Qwen2.5-VL-3B-Instruct" \
    --max-model-len 8192 \
    --host 0.0.0.0 \
    --port 8000 \
    --dtype float16