#!/bin/bash

# Script d'installation et de configuration de Rizinova-AI

set -e

echo "=================================="
echo "🚀 Installation Rizinova-AI"
echo "=================================="

# Étape 1: Vérifier Python
echo "\n1️⃣ Vérification de Python..."
python --version

# Étape 2: Créer l'environnement virtuel
echo "\n2️⃣ Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel déjà existant"
fi

# Activer l'environnement
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Environnement virtuel activé"

# Étape 3: Installer les dépendances
echo "\n3️⃣ Installation des dépendances..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dépendances installées"

# Étape 4: Configurer l'environnement
echo "\n4️⃣ Configuration de l'environnement..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Fichier .env créé depuis .env.example"
    echo "⚠️  Veuillez éditer .env avec vos vraies clés API"
else
    echo "✅ Fichier .env déjà existant"
fi

# Étape 5: Créer le répertoire logs
echo "\n5️⃣ Création du répertoire logs..."
mkdir -p logs
echo "✅ Répertoire logs créé"

# Étape 6: Migrations Django
echo "\n6️⃣ Exécution des migrations Django..."
python manage.py migrate
echo "✅ Migrations exécutées"

# Étape 7: Collecter les fichiers statiques
echo "\n7️⃣ Collection des fichiers statiques..."
python manage.py collectstatic --noinput
echo "✅ Fichiers statiques collectés"

# Étape 8: Exécuter les tests
echo "\n8️⃣ Exécution des tests..."
pytest --cov=apps --cov-report=html --cov-report=term-missing
echo "✅ Tests exécutés (rapport HTML dans htmlcov/)"

echo "\n=================================="
echo "✅ Installation terminée!"
echo "=================================="
echo ""
echo "📋 Prochaines étapes:"
echo "1. Éditer backend/.env avec vos clés API"
echo "2. Démarrer le serveur: python manage.py runserver"
echo "3. Accéder au health check: http://localhost:8000/api/health/"
echo ""
