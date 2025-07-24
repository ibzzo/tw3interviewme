"""
Service Hugging Face pour utiliser Qwen2.5-32B-Instruct
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import os

logger = logging.getLogger(__name__)


class HuggingFaceService:
    """Service pour utiliser le modèle Qwen via Hugging Face"""
    
    def __init__(self):
        """Initialise le service avec le modèle Qwen"""
        self.model_name = "Qwen/Qwen2.5-32B-Instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🤖 Initialisation du modèle {self.model_name}")
        logger.info(f"🖥️ Device: {self.device}")
        
        try:
            # Pour économiser la mémoire, on utilise le pipeline qui gère automatiquement
            # le chargement et l'optimisation
            self.pipe = pipeline(
                "text-generation",
                model=self.model_name,
                device=self.device,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                # Limiter l'utilisation mémoire
                model_kwargs={
                    "load_in_8bit": True if self.device == "cuda" else False,
                    "low_cpu_mem_usage": True
                }
            )
            logger.info("✅ Modèle chargé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
            # Fallback vers un modèle plus petit si nécessaire
            logger.info("🔄 Tentative avec un modèle plus petit...")
            self.model_name = "Qwen/Qwen2.5-7B-Instruct"
            try:
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model_name,
                    device=self.device,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                )
                logger.info(f"✅ Modèle de fallback {self.model_name} chargé")
            except Exception as e2:
                logger.error(f"❌ Impossible de charger le modèle: {e2}")
                raise
    
    def generate_response(
        self, 
        query: str, 
        search_results: Optional[List[Dict]] = None,
        current_date: Optional[datetime] = None,
        time_constraint: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Génère une réponse en utilisant le modèle Qwen
        """
        logger.info(f"\n🤖 HUGGING FACE - Génération de réponse")
        logger.info(f"📊 Modèle: {self.model_name}")
        
        try:
            messages = []
            
            # Si des résultats de recherche sont fournis
            if search_results:
                system_content = self._create_system_prompt_with_context(
                    search_results, 
                    current_date, 
                    time_constraint
                )
                messages.append({
                    "role": "system",
                    "content": system_content
                })
                
                # Ajouter l'historique si présent
                if conversation_history:
                    for msg in conversation_history[-3:]:  # Derniers 3 messages pour économiser les tokens
                        if msg['role'] in ['user', 'assistant']:
                            messages.append({
                                "role": msg['role'],
                                "content": msg['content']
                            })
            else:
                # Sans recherche web
                messages.append({
                    "role": "system",
                    "content": "Tu es un assistant IA utile et amical. Réponds de manière claire et concise en français."
                })
                
                if conversation_history:
                    for msg in conversation_history[-3:]:
                        if msg['role'] in ['user', 'assistant']:
                            messages.append({
                                "role": msg['role'],
                                "content": msg['content']
                            })
            
            # Ajouter la question actuelle
            messages.append({
                "role": "user",
                "content": query
            })
            
            logger.info(f"📝 Nombre de messages: {len(messages)}")
            
            # Générer la réponse
            outputs = self.pipe(
                messages,
                max_new_tokens=1500,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                return_full_text=False
            )
            
            # Extraire la réponse
            response = outputs[0]['generated_text']
            
            # Valider l'utilisation des sources si recherche
            if search_results and not self._validate_source_usage(response, search_results):
                logger.warning("⚠️ Réponse sans citations suffisantes")
                response = self._add_source_reminder(response, search_results)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur Hugging Face: {str(e)}")
            return f"Désolé, une erreur s'est produite lors de la génération de la réponse: {str(e)}"
    
    def _create_system_prompt_with_context(
        self, 
        search_results: List[Dict], 
        current_date: Optional[datetime],
        time_constraint: Optional[str]
    ) -> str:
        """Crée un prompt système avec le contexte de recherche"""
        
        # Informations temporelles
        date_info = ""
        if current_date:
            date_info = f"""
📅 DATE ACTUELLE: {current_date.strftime('%d/%m/%Y')}
📅 SEMAINE ACTUELLE: Semaine {current_date.isocalendar()[1]} de {current_date.year}
⏰ PÉRIODE DEMANDÉE: {time_constraint or 'Non spécifiée'}
"""
        
        # Formater le contexte
        context = self._format_search_results(search_results)
        
        # Prompt système
        system_prompt = f"""Tu es un assistant IA expert en actualités technologiques. Tu DOIS utiliser EXCLUSIVEMENT les informations fournies dans le contexte de recherche ci-dessous.
{date_info}

🔴 RÈGLES OBLIGATOIRES:
1. Base ta réponse UNIQUEMENT sur le contexte fourni
2. Cite chaque information avec [Source: Titre]
3. Si une info n'est pas dans le contexte, dis-le clairement
4. Termine par "📚 Sources consultées:" avec les URLs

📰 CONTEXTE DE RECHERCHE:
{context}

⚠️ RAPPEL: Utilise UNIQUEMENT les informations ci-dessus."""
        
        return system_prompt
    
    def _format_search_results(self, search_results: List[Dict]) -> str:
        """Formate les résultats de recherche"""
        if not search_results:
            return "Aucun résultat disponible."
        
        formatted = []
        for i, result in enumerate(search_results[:8], 1):  # Max 8 pour limiter les tokens
            title = result.get('title', 'Sans titre')
            url = result.get('url', '#')
            content = result.get('content', 'Non disponible')[:300]  # Limiter la longueur
            date = result.get('date', 'Date non spécifiée')
            
            formatted.append(f"""
=== RÉSULTAT {i} ===
📰 {title}
📅 {date}
🔗 {url}
📝 {content}...
""")
        
        return "\n".join(formatted)
    
    def _validate_source_usage(self, response: str, search_results: List[Dict]) -> bool:
        """Vérifie que la réponse utilise les sources"""
        response_lower = response.lower()
        
        # Patterns de citation
        citation_patterns = ["[source:", "source:", "selon", "d'après", "sources consultées"]
        
        # Compter les citations
        citation_count = sum(1 for pattern in citation_patterns if pattern in response_lower)
        
        # Vérifier si au moins 30% des sources sont citées
        min_citations = max(1, len(search_results) // 3)
        
        return citation_count >= min_citations
    
    def _add_source_reminder(self, response: str, search_results: List[Dict]) -> str:
        """Ajoute les sources si non citées"""
        
        if "sources consultées" in response.lower():
            return response
        
        # Ajouter une section sources
        sources_section = "\n\n📚 **Sources consultées:**\n"
        for i, result in enumerate(search_results[:5], 1):
            title = result.get('title', 'Sans titre')
            url = result.get('url', '#')
            sources_section += f"{i}. {title}\n   🔗 {url}\n"
        
        return response + sources_section