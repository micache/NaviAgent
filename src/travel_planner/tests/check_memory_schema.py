"""Check user_memories table schema for created_at column"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import get_db
from sqlalchemy import text


def check_memory_table():
    print("=" * 80)
    print("Checking user_memories table schema")
    print("=" * 80)

    db = get_db()
    engine = db.db_engine
    schema = db.db_schema
    table = db.memory_table_name

    with engine.connect() as conn:
        # Get column info
        result = conn.execute(
            text(
                """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table
            ORDER BY ordinal_position
        """
            ),
            {"schema": schema, "table": table},
        )

        print(f"\nTable: {schema}.{table}")
        print("\nColumns:")
        print(f"{'Column':<20} {'Type':<20} {'Nullable':<10}")
        print("-" * 50)

        has_created_at = False
        for row in result:
            col_name, data_type, nullable = row
            print(f"{col_name:<20} {data_type:<20} {nullable:<10}")
            if col_name == "created_at":
                has_created_at = True

        print("\n" + "=" * 80)
        if has_created_at:
            print("⚠️  PROBLEM FOUND: Table has 'created_at' column")
            print("   But UserMemory class only expects these fields:")
            print("   - memory, memory_id, topics, user_id, input, updated_at")
            print("   - feedback, agent_id, team_id")
            print(
                "\n   SOLUTION: SafePostgresDb strips 'created_at' before deserialization"
            )
        else:
            print("✓ Table schema is correct (no created_at column)")

        # Check actual data
        print("\n" + "=" * 80)
        print("Sample data:")
        result = conn.execute(text(f"SELECT * FROM {schema}.{table} LIMIT 2"))

        if result.rowcount == 0:
            print("  (No data yet)")
        else:
            for i, row in enumerate(result, 1):
                print(f"\nRow {i}:")
                row_dict = dict(row._mapping)
                for key, value in row_dict.items():
                    if len(str(value)) > 100:
                        print(f"  {key}: {str(value)[:100]}...")
                    else:
                        print(f"  {key}: {value}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        check_memory_table()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
