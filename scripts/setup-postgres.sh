#!/usr/bin/env bash
# Local PostgreSQL setup for Solar Plant Intelligence (run once on Ubuntu).
set -euo pipefail

echo "Installing PostgreSQL (requires sudo)..."
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

echo "Starting PostgreSQL..."
sudo systemctl enable --now postgresql

DB_NAME="solar_plant_intelligence"
DB_USER="solar_app"
DB_PASS="solar_dev"

echo "Creating role and database (run as postgres superuser)..."
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL

echo "Done. Use DATABASE_URL from backend/.env.example"
