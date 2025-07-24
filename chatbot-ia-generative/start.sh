#!/bin/bash

echo "🚀 Démarrage du Chatbot IA Générative..."

# Vérifier si Redis est installé et le démarrer si possible
if command -v redis-server &> /dev/null; then
    echo "📦 Démarrage de Redis..."
    redis-server --daemonize yes
fi

# Activer l'environnement virtuel
echo "🐍 Activation de l'environnement Python..."
source venv/bin/activate

# Démarrer le backend Django
echo "🔧 Démarrage du backend Django..."
python manage.py runserver &
BACKEND_PID=$!

# Attendre que le backend soit prêt
sleep 5

# Démarrer le frontend React
echo "⚛️  Démarrage du frontend React..."
cd frontend
npm start &
FRONTEND_PID=$!

echo "✅ Application démarrée !"
echo "📍 Backend: http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "Pour arrêter l'application, appuyez sur Ctrl+C"

# Attendre et nettoyer à la sortie
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; redis-cli shutdown 2>/dev/null" EXIT
wait