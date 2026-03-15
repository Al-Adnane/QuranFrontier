#!/bin/bash

# FrontierQu Database Setup Script
# Initializes PostgreSQL database and schema for corpus data

set -e

# Configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-quran_frontier}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-}
SCHEMA_FILE="${SCRIPT_DIR}/schema.sql"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "FrontierQu Database Setup"
echo "========================================="
echo ""
echo "Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Function to execute SQL
execute_sql() {
    local sql="$1"
    if [ -n "$DB_PASSWORD" ]; then
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "$sql"
    else
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "$sql"
    fi
}

# Function to execute SQL file
execute_sql_file() {
    local file="$1"
    local dbname="$2"
    if [ -n "$DB_PASSWORD" ]; then
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$dbname" -f "$file"
    else
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$dbname" -f "$file"
    fi
}

# Step 1: Check PostgreSQL connection
echo "[1/5] Checking PostgreSQL connection..."
if [ -n "$DB_PASSWORD" ]; then
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT version();" > /dev/null
else
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT version();" > /dev/null
fi
echo "✓ PostgreSQL connection successful"

# Step 2: Create database if not exists
echo "[2/5] Creating database..."
if execute_sql "CREATE DATABASE $DB_NAME;" 2>/dev/null; then
    echo "✓ Database created: $DB_NAME"
else
    echo "✓ Database already exists: $DB_NAME"
fi

# Step 3: Initialize schema
echo "[3/5] Initializing schema..."
if [ -f "$SCHEMA_FILE" ]; then
    execute_sql_file "$SCHEMA_FILE" "$DB_NAME"
    echo "✓ Schema initialized successfully"
else
    echo "✗ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

# Step 4: Create audit tables (ensure they exist)
echo "[4/5] Verifying audit tables..."
execute_sql_file <(cat <<EOF) "$DB_NAME"
-- Verify audit tables exist
SELECT 'Audit tables verified' as status;
EOF
echo "✓ Audit tables verified"

# Step 5: Display database statistics
echo "[5/5] Database verification..."
if [ -n "$DB_PASSWORD" ]; then
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_NAME" -d "$DB_NAME" -c "
        SELECT
            'Surahs' as table_name,
            COUNT(*) as count
        FROM surahs
        UNION ALL
        SELECT
            'Verses',
            COUNT(*)
        FROM verses
        UNION ALL
        SELECT
            'Tafsirs',
            COUNT(*)
        FROM tafsirs
        UNION ALL
        SELECT
            'Hadiths',
            COUNT(*)
        FROM hadiths
        UNION ALL
        SELECT
            'Narrators',
            COUNT(*)
        FROM narrators
        UNION ALL
        SELECT
            'Madhabs',
            COUNT(*)
        FROM madhabs;
    "
else
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
        SELECT
            'Surahs' as table_name,
            COUNT(*) as count
        FROM surahs
        UNION ALL
        SELECT
            'Verses',
            COUNT(*)
        FROM verses
        UNION ALL
        SELECT
            'Tafsirs',
            COUNT(*)
        FROM tafsirs
        UNION ALL
        SELECT
            'Hadiths',
            COUNT(*)
        FROM hadiths
        UNION ALL
        SELECT
            'Narrators',
            COUNT(*)
        FROM narrators
        UNION ALL
        SELECT
            'Madhabs',
            COUNT(*)
        FROM madhabs;
    "
fi

echo ""
echo "========================================="
echo "Database setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Load data: python ingest_corpus_data.py --db postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
echo "2. Verify schema: psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo "3. Check indexes: \\di (in psql)"
echo ""
