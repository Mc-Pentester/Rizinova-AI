# CHANGELOG - Rizinova-AI Improvements

## Version 1.1.0 - Security & Logging Enhancements

### 🚀 Nouvelles Fonctionnalités

#### Base de Données
- ✅ Migration de SQLite vers PostgreSQL
- ✅ Support multi-utilisateurs et transactionnel
- ✅ Configuration via variables d'environnement

#### Authentification & Sécurité
- ✅ Authentification JWT (tokens access + refresh)
- ✅ Rate limiting (100/h anonyme, 1000/h authentifié)
- ✅ En-têtes de sécurité avancés (HSTS, CSP, X-Frame-Options)
- ✅ Validation des credentials en production

#### Journalisation
- ✅ Logs structurés en JSON
- ✅ Rotation automatique des fichiers (10 MB max)
- ✅ Loggers séparés : django.log, api.log, security.log
- ✅ Middleware de logging des requêtes/réponses API

#### Documentation API
- ✅ Swagger/OpenAPI auto-généré avec drf-spectacular
- ✅ Endpoints: /api/schema/swagger/ et /api/schema/redoc/
- ✅ Serializers pour validation des données

#### Middleware Avancé
- ✅ IgnoreBrokenPipeMiddleware : Gestion des déconnexions
- ✅ APILoggingMiddleware : Journalisation détaillée
- ✅ SecurityHeadersMiddleware : En-têtes supplémentaires
- ✅ RateLimitingMiddleware : Limitation par IP

#### Tests Étendus (24 tests total)
- ✅ RAG Embedder (4 tests)
- ✅ Knowledge Documents (5 tests)
- ✅ RAG Integration (4 tests)
- ✅ API Authentication (3 tests)
- ✅ Rate Limiting (2 tests)
- ✅ Security Headers (1 test)
- ✅ Logging (3 tests)
- ✅ Database Configuration (2 tests)

### 📦 Nouvelles Dépendances

```
- django-ratelimit>=4.1.0          # Rate limiting
- djangorestframework-simplejwt>=5.3.0  # JWT Auth
- drf-spectacular>=0.27.0          # API Documentation
- python-logging-loki>=0.3.2       # Structured logging
- structlog>=24.1.0                # JSON logging
- gunicorn>=21.2.0                 # Production server
- whitenoise>=6.6.0                # Static files serving
```

### 🔐 Sécurité Améliorée

| Aspect | Avant | Après |
|--------|-------|-------|
| Base de données | SQLite (développement) | PostgreSQL (production) |
| Authentification API | Aucune | JWT |
| Rate limiting | Aucun | 100/h (anon), 1000/h (user) |
| Logging | Basique | Structuré JSON + rotation |
| Documentation | Aucune | Swagger/OpenAPI |
| Sécurité | De base | HSTS, CSP, X-Frame-Options |
| Headers | Standards | Renforcés |

### 📊 Configuration Base de Données

```bash
# PostgreSQL Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=rizinova_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
```

### 📡 API Endpoints Documentés

- `GET /api/health/` - Health check (AllowAny)
- `POST /api/search/` - Recherche RAG (IsAuthenticated)
- `GET /api/profile/` - Profil utilisateur (IsAuthenticated)
- `GET /api/quota/` - Statut quota (IsAuthenticated)

### 🧪 Exécution des Tests

```bash
cd backend
pytest --cov=apps --cov-report=html
python manage.py test
python run_tests.sh
```

### 📖 Documentation

- Swagger: `/api/schema/swagger/`
- ReDoc: `/api/schema/redoc/`
- Logs: `logs/django.log`, `logs/api.log`, `logs/security.log`

### 🚀 Déploiement

**Développement:**
```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

**Production:**
```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### ⚠️ Notes Importantes

1. PostgreSQL doit être installé et accessible
2. Tous les développeurs doivent mettre à jour `.env`
3. Redémarrage du serveur après merge
4. Tests doivent passer avant déploiement

### 📝 Fichiers Modifiés

- `backend/config/settings.py` - Configuration Django complète
- `backend/requirements.txt` - Dépendances mises à jour
- `backend/.env.example` - Variables d'environnement
- `backend/apps/core/middleware.py` - Middleware avancé
- `backend/apps/knowledge/api.py` - Endpoints REST
- `backend/tests.py` - Tests étendus (24 tests)
- `PULL_REQUEST_TEMPLATE.md` - Template pour PRs futures

### 🎯 Checklist de Production

- [ ] PostgreSQL configuré et accessible
- [ ] `.env` mis à jour avec credentials
- [ ] Tests passent (24/24)
- [ ] Migrations appliquées
- [ ] Logs configurés et testés
- [ ] JWT tokens générés et testés
- [ ] Rate limiting validé
- [ ] Documentation API accessible
- [ ] Fichiers statiques servés avec WhiteNoise
- [ ] Certificats SSL activés (si nécessaire)

---

**Date:** 3 juin 2026
**Branche:** `improvements/enhance-security-logging`
**Statut:** ✅ Prêt pour review et merge
