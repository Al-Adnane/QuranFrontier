#!/usr/bin/env python3
"""
Schema Validation Script
Validates database schema integrity and completeness
"""

import sys
import psycopg2
from psycopg2 import sql


def check_schema(db_url: str):
    """Validate database schema"""
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("=" * 70)
        print("SCHEMA VALIDATION REPORT")
        print("=" * 70)

        # Check tables exist
        print("\n[1] TABLE EXISTENCE CHECK")
        print("-" * 70)

        expected_tables = [
            'surahs', 'verses', 'tafsir_scholars', 'tafsir_editions', 'tafsirs',
            'hadith_collections', 'hadiths', 'narrators', 'narrator_chains',
            'madhabs', 'verse_madhab_links', 'sources',
            'data_audit_log', 'bulk_load_metadata'
        ]

        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
        """)
        existing_tables = {row[0] for row in cursor.fetchall()}

        missing_tables = set(expected_tables) - existing_tables
        extra_tables = existing_tables - set(expected_tables)

        for table in expected_tables:
            status = "✓" if table in existing_tables else "✗"
            print(f"  {status} {table}")

        if missing_tables:
            print(f"\n  WARNING: Missing tables: {missing_tables}")
        if extra_tables:
            print(f"\n  NOTE: Extra tables found: {extra_tables}")

        # Check indexes
        print("\n[2] INDEX CHECK")
        print("-" * 70)

        cursor.execute("""
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)

        indexes = cursor.fetchall()
        index_count_by_table = {}
        for tablename, indexname, _ in indexes:
            index_count_by_table[tablename] = index_count_by_table.get(tablename, 0) + 1

        for table in sorted(index_count_by_table.keys()):
            print(f"  {table}: {index_count_by_table[table]} indexes")

        # Check views
        print("\n[3] VIEW CHECK")
        print("-" * 70)

        cursor.execute("""
            SELECT viewname FROM pg_views
            WHERE schemaname = 'public'
            ORDER BY viewname
        """)

        views = cursor.fetchall()
        if views:
            for view, in views:
                print(f"  ✓ {view}")
        else:
            print("  No views found")

        # Check functions/triggers
        print("\n[4] TRIGGER FUNCTIONS CHECK")
        print("-" * 70)

        cursor.execute("""
            SELECT proname FROM pg_proc
            WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY proname
        """)

        functions = cursor.fetchall()
        if functions:
            for func, in functions:
                print(f"  ✓ {func}")
        else:
            print("  No functions found")

        # Check constraints
        print("\n[5] CONSTRAINT CHECK")
        print("-" * 70)

        cursor.execute("""
            SELECT
                tc.table_name,
                constraint_name,
                constraint_type
            FROM information_schema.table_constraints tc
            WHERE table_schema = 'public'
            ORDER BY table_name, constraint_name
        """)

        constraints = cursor.fetchall()
        constraint_by_table = {}
        for table, constraint, ctype in constraints:
            if table not in constraint_by_table:
                constraint_by_table[table] = []
            constraint_by_table[table].append((constraint, ctype))

        for table in sorted(constraint_by_table.keys()):
            print(f"  {table}:")
            for constraint, ctype in constraint_by_table[table]:
                print(f"    - {constraint} ({ctype})")

        # Check data (if any)
        print("\n[6] DATA PRESENCE CHECK")
        print("-" * 70)

        for table in ['surahs', 'verses', 'tafsirs', 'hadiths', 'narrators', 'madhabs']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "✓" if count > 0 else "○"
            print(f"  {status} {table}: {count:,} records")

        # Column definitions
        print("\n[7] CRITICAL COLUMNS CHECK")
        print("-" * 70)

        critical_columns = {
            'verses': ['verse_id', 'quran_id', 'surah', 'ayah', 'text_arabic', 'hash_sha256'],
            'hadiths': ['hadith_id', 'collection_id', 'hadith_text_arabic', 'grade', 'hash_sha256'],
            'tafsirs': ['tafsir_id', 'verse_id', 'text_arabic', 'hash_sha256'],
            'narrators': ['narrator_id', 'name_arabic', 'reliability_grade'],
        }

        for table, columns in critical_columns.items():
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
            """, (table,))
            existing_cols = {row[0] for row in cursor.fetchall()}

            print(f"  {table}:")
            for col in columns:
                status = "✓" if col in existing_cols else "✗"
                print(f"    {status} {col}")

        # Extensions
        print("\n[8] EXTENSIONS CHECK")
        print("-" * 70)

        cursor.execute("""
            SELECT extname FROM pg_extension
            ORDER BY extname
        """)

        extensions = cursor.fetchall()
        if extensions:
            for ext, in extensions:
                print(f"  ✓ {ext}")
        else:
            print("  No extensions found")

        # Summary
        print("\n" + "=" * 70)
        print("VALIDATION COMPLETE")
        print("=" * 70)
        print("\nSchema appears to be:")
        issues = len(missing_tables) + len([t for t, c in [(t, c) for t, columns in critical_columns.items()
                                                            for c in columns
                                                            if c not in {row[0] for row in cursor.fetchall()}]])
        if issues == 0:
            print("  ✓ VALID - All checks passed")
        else:
            print(f"  ✗ INVALID - {issues} issues found")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        return False

    return True


if __name__ == '__main__':
    db_url = sys.argv[1] if len(sys.argv) > 1 else 'postgresql://localhost/quran_frontier'
    success = check_schema(db_url)
    sys.exit(0 if success else 1)
