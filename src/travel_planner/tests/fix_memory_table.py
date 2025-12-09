"""Remove created_at column from user_memories table"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import get_db
from sqlalchemy import text


def fix_memory_table():
    print("=" * 80)
    print("Fixing user_memories table schema")
    print("=" * 80)

    db = get_db()
    engine = db.db_engine
    schema = db.db_schema
    table = db.memory_table_name

    print(f"\n⚠️  This will remove the 'created_at' column from {schema}.{table}")
    print("   (Agno's UserMemory class doesn't use this field)")

    response = input("\nContinue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        return

    with engine.connect() as conn:
        with conn.begin():
            # Drop created_at column
            conn.execute(
                text(f"ALTER TABLE {schema}.{table} DROP COLUMN IF EXISTS created_at")
            )
            print(f"\n✓ Dropped 'created_at' column from {schema}.{table}")

        # Verify
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table
            ORDER BY ordinal_position
        """
            ),
            {"schema": schema, "table": table},
        )

        print("\nCurrent columns:")
        for row in result:
            print(f"  - {row[0]}")

    print("\n" + "=" * 80)
    print("✓ Table fixed! You can now use the database without errors.")
    print("=" * 80)


if __name__ == "__main__":
    try:
        fix_memory_table()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
