#!/bin/bash

# Script de démarrage du serveur de développement

set -e

echo "=================================="
echo "🚀 Démarrage du serveur Rizinova-AI"
echo "=================================="

cd backend

echo "\n✅ Configuration en cours de vérification..."

if [ ! -f ".env" ]; then
    echo "❌ Erreur: Fichier .env non trouvé"
    echo "Veuillez d'abord exécuter: cp .env.example .env"
    exit 1
fi

echo "\n✅ Fichier .env trouvé"
echo "\n📁 Vérification du répertoire logs..."
mkdir -p logs

echo "\n🔍 Vérification de la base de données..."
python manage.py check

echo "\n📊 Vérification du health check..."
python manage.py shell -c "
from apps.core.monitoring import HealthCheck
import json
health = HealthCheck.get_full_health_check()
print('\n=== HEALTH CHECK ===')
print(json.dumps(health, indent=2))
print('\n')
"

echo "\n🌐 Démarrage du serveur sur http://localhost:8000"
echo "📍 Health Check disponible sur http://localhost:8000/api/health/"
echo "💻 Admin disponible sur http://localhost:8000/admin/"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur\n"

python manage.py runserver 0.0.0.0:8000
