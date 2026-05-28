#!/bin/bash

# Script d'exécution des tests avec rapport détaillé

set -e

echo "=================================="
echo "🧪 Exécution des tests Rizinova-AI"
echo "=================================="

cd backend

echo "\n1️⃣ Tests unitaires..."
pytest apps/knowledge/tests/test_rag_service.py -v

echo "\n2️⃣ Tests d'authentification..."
pytest apps/knowledge/tests/test_authentication.py -v

echo "\n3️⃣ Tests du système de quota..."
pytest apps/knowledge/tests/test_quota_system.py -v

echo "\n4️⃣ Tests des APIs..."
pytest apps/knowledge/tests/test_api.py -v

echo "\n5️⃣ Rapport de couverture..."
pytest --cov=apps --cov-report=html --cov-report=term-missing

echo ""
echo "=================================="
echo "✅ Tests terminés!"
echo "=================================="
echo ""
echo "📊 Rapport HTML disponible: htmlcov/index.html"
echo ""
