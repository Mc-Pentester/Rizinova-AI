#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.monitoring import HealthCheck, PerformanceMonitor
import json

def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")

def test_health_check():
    """Test le health check complet"""
    print_header("🏥 TEST HEALTH CHECK")
    
    health = HealthCheck.get_full_health_check()
    print(json.dumps(health, indent=2))
    
    if health['status'] == 'healthy':
        print("\n✅ Status: HEALTHY")
        return True
    else:
        print("\n❌ Status: UNHEALTHY")
        return False

def test_system_stats():
    """Affiche les statistiques système"""
    print_header("💻 STATISTIQUES SYSTÈME")
    
    stats = PerformanceMonitor.get_system_stats()
    print(json.dumps(stats, indent=2))

def test_logging():
    """Test le système de logging"""
    print_header("📝 TEST LOGGING")
    
    import logging
    logger = logging.getLogger('apps.knowledge.rag_service')
    
    logger.debug("📌 Message de DEBUG")
    logger.info("ℹ️  Message d'INFO")
    logger.warning("⚠️  Message d'WARNING")
    logger.error("❌ Message d'ERROR")
    
    print("✅ Messages de log envoyés. Consultez:")
    print("   - logs/app.log")
    print("   - logs/rag.log")
    print("   - logs/errors.log")

def test_database():
    """Test la connexion à la base de données"""
    print_header("🗄️  TEST BASE DE DONNÉES")
    
    ok, msg = HealthCheck.check_database()
    if ok:
        print(f"✅ {msg}")
        
        # Afficher les statistiques
        from django.contrib.auth.models import User
        from apps.knowledge.models import KnowledgeDocument
        
        print(f"\n   Utilisateurs: {User.objects.count()}")
        print(f"   Documents: {KnowledgeDocument.objects.count()}")
    else:
        print(f"❌ {msg}")

def test_storage_backend():
    """Test le backend de stockage"""
    print_header("📦 TEST BACKEND DE STOCKAGE")
    
    ok, msg = HealthCheck.check_storage_backend()
    if ok:
        print(f"✅ {msg}")
    else:
        print(f"❌ {msg}")

if __name__ == '__main__':
    print("\n")
    print("█████████████████████████████████████████")
    print("   🚀 DIAGNOSTIC RIZINOVA-AI")
    print("█████████████████████████████████████████")
    
    test_health_check()
    test_system_stats()
    test_database()
    test_storage_backend()
    test_logging()
    
    print_header("✅ DIAGNOSTIC TERMINÉ")
    print("\n📋 Fichiers de log: backend/logs/\n")
