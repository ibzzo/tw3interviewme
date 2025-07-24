#!/usr/bin/env python3
"""
Demo script pour Vision Language Model (VLM) - Partie 3
Utilise UNIQUEMENT Qwen/Qwen2.5-VL-3B-Instruct en local
"""

import sys
import os

def install_vllm():
    """Guide d'installation pour vLLM."""
    print("="*60)
    print("🎯 Installation de vLLM pour Qwen2.5-VL")
    print("="*60)
    print()
    print("⚠️  IMPORTANT: vLLM nécessite Python 3.8-3.12 (pas 3.13)")
    print()
    print("📦 Étapes d'installation:")
    print()
    print("1. Créer un environnement Python 3.12:")
    print("   brew install python@3.12")
    print("   python3.12 -m venv venv_vlm")
    print("   source venv_vlm/bin/activate")
    print()
    print("2. Installer vLLM:")
    print("   pip install vllm")
    print()
    print("3. Lancer le serveur vLLM:")
    print("   vllm serve 'Qwen/Qwen2.5-VL-3B-Instruct'")
    print()
    print("4. Dans un autre terminal, exécuter ce script:")
    print("   python vlm_demo.py <image>")
    print("="*60)

def test_vllm_server():
    """Teste si le serveur vLLM est actif."""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def process_image_with_qwen_vl(image_path, prompt="Describe this image in detail."):
    """Traite une image avec Qwen2.5-VL via vLLM."""
    try:
        import requests
        import base64
        from PIL import Image
        import io
    except ImportError:
        print("❌ Dépendances manquantes. Installer:")
        print("   pip install requests pillow")
        sys.exit(1)
    
    # Vérifier le serveur
    if not test_vllm_server():
        print("❌ Le serveur vLLM n'est pas démarré!")
        print("   Lancez d'abord: vllm serve 'Qwen/Qwen2.5-VL-3B-Instruct'")
        return None
    
    # Préparer l'image
    if image_path.startswith('http'):
        # URL
        image_url = image_path
    else:
        # Fichier local -> base64
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionner si trop grande
            max_size = 1024
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size))
            
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{base64_image}"
    
    # Préparer la requête pour vLLM
    data = {
        "model": "Qwen/Qwen2.5-VL-3B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    # Envoyer la requête avec animation de chargement
    import threading
    import time
    
    print("🤖 Envoi de la requête à Qwen2.5-VL...")
    
    # Animation de chargement
    stop_loading = False
    def loading_animation():
        chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        idx = 0
        while not stop_loading:
            print(f'\r{chars[idx % len(chars)]} Traitement en cours...', end='', flush=True)
            idx += 1
            time.sleep(0.1)
        print('\r✅ Traitement terminé!     ', flush=True)
    
    # Démarrer l'animation dans un thread séparé
    loading_thread = threading.Thread(target=loading_animation)
    loading_thread.start()
    
    try:
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes pour CPU
        )
    finally:
        stop_loading = True
        loading_thread.join()
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"Erreur: {response.status_code} - {response.text}"

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python vlm_demo.py <image_path> [prompt]")
        print("\nExemples:")
        print("  python vlm_demo.py photo.jpg")
        print("  python vlm_demo.py photo.jpg 'Extract all text from this image'")
        print()
        install_vllm()
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Describe this image in detail. If there is text, extract it."
    
    print("="*60)
    print("🎯 Qwen2.5-VL Demo")
    print("="*60)
    print(f"📷 Image: {image_path}")
    print(f"💬 Prompt: {prompt}")
    print()
    
    # Vérifier que l'image existe
    if not image_path.startswith('http') and not os.path.exists(image_path):
        print(f"❌ L'image '{image_path}' n'existe pas")
        sys.exit(1)
    
    # Traiter l'image
    result = process_image_with_qwen_vl(image_path, prompt)
    
    if result:
        print("\n📝 Résultat Qwen2.5-VL:")
        print("-"*60)
        print(result)
        print("-"*60)
    else:
        print("\n⚠️  Assurez-vous que le serveur vLLM est démarré:")
        print("   vllm serve 'Qwen/Qwen2.5-VL-3B-Instruct'")

if __name__ == "__main__":
    main()