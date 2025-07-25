import os
import logging
from typing import Dict, List, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class VLLMService:
    """Service pour interagir avec vLLM (LLM local haute performance)"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'VLLM_BASE_URL', 'http://localhost:8000')
        self.model = getattr(settings, 'VLLM_MODEL', 'meta-llama/Llama-3.2-3B-Instruct')
        self.timeout = 300  # 5 minutes pour CPU
        
    def is_available(self) -> bool:
        """Vérifie si vLLM est disponible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> Dict:
        """Génère une réponse avec vLLM en utilisant l'API compatible OpenAI"""
        try:
            # Construire les messages
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Utilise ce contexte de recherche web pour répondre: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Préparer la requête compatible OpenAI
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,  # Réduit pour CPU
                "top_p": 0.9
            }
            
            # Envoyer la requête à l'endpoint compatible OpenAI
            url = f"{self.base_url}/v1/chat/completions"
            logger.info(f"🚀 Envoi requête vLLM vers: {url}")
            logger.info(f"⏱️ Mode CPU: cela peut prendre 1-2 minutes...")
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extraire la réponse du format OpenAI
                content = data['choices'][0]['message']['content']
                return {
                    "success": True,
                    "response": content,
                    "model": self.model,
                    "provider": "vllm_local",
                    "usage": data.get('usage', {})
                }
            else:
                logger.error(f"Erreur vLLM: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Erreur du serveur vLLM: {response.status_code}",
                    "provider": "vllm_local"
                }
                
        except requests.Timeout:
            logger.error("Timeout lors de la génération avec vLLM")
            return {
                "success": False,
                "error": "Le modèle local a mis trop de temps à répondre",
                "provider": "vllm_local"
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "vllm_local"
            }
    
    def generate_streaming_response(self, prompt: str, context: Optional[str] = None):
        """Génère une réponse en streaming avec vLLM"""
        try:
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Utilise ce contexte de recherche web pour répondre: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": True
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                stream=True,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        # Décoder les événements SSE
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # Retirer "data: "
                            if data_str == '[DONE]':
                                break
                            try:
                                import json
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                yield f"Erreur: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Erreur streaming: {e}")
            yield f"Erreur: {str(e)}"
    
    def list_models(self) -> List[str]:
        """Liste les modèles disponibles (vLLM sert généralement un seul modèle)"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            return [self.model]  # Retourner le modèle configuré par défaut
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return [self.model]