#!/bin/bash

# Script de backup PostgreSQL automatisé pour Rizinova-AI
# Utilisation: ./backup_database.sh

set -e

# Configuration
BACKUP_DIR="./backups"
DB_NAME="${DB_NAME:-rizinova}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
RETENTION_DAYS=30

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Créer le dossier de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql.gz"

echo -e "${YELLOW}▶️ Démarrage du backup PostgreSQL...${NC}"
echo "Base de données: $DB_NAME"
echo "Fichier: $BACKUP_FILE"

# Effectuer le backup
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    echo -e "${GREEN}✅ Backup réussi!${NC}"
    ls -lh "$BACKUP_FILE"
else
    echo -e "${RED}❌ Erreur lors du backup${NC}"
    exit 1
fi

# Nettoyer les anciens backups
echo -e "${YELLOW}▶️ Nettoyage des anciens backups (> $RETENTION_DAYS jours)...${NC}"
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime "+$RETENTION_DAYS" -delete

# Compter les backups restants
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" | wc -l)
echo -e "${GREEN}✅ Nettoyage terminé. Backups conservés: $BACKUP_COUNT${NC}"

# Optionnel: Envoyer vers le cloud (S3, Google Cloud, etc.)
# aws s3 cp "$BACKUP_FILE" "s3://my-bucket/backups/"

echo -e "${GREEN}✅ Backup terminé avec succès!${NC}"
