import sqlite3
import os

db_path = 'soundit_local.db'

print(f"Applying SQLite schema alterations to: {db_path}")
if not os.path.exists(db_path):
    print("Error: soundit_local.db file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(venue_profiles)")
existing_cols = [row[1] for row in cursor.fetchall()]

# Add menu_items if it doesn't exist
if 'menu_items' not in existing_cols:
    try:
        print("Adding column 'menu_items' to 'venue_profiles'...")
        cursor.execute("ALTER TABLE venue_profiles ADD COLUMN menu_items JSON DEFAULT '[]'")
        conn.commit()
        print("Added column 'menu_items' successfully.")
    except Exception as e:
        print(f"Error adding 'menu_items': {e}")
else:
    print("Column 'menu_items' already exists.")

# Add table_configs if it doesn't exist
if 'table_configs' not in existing_cols:
    try:
        print("Adding column 'table_configs' to 'venue_profiles'...")
        cursor.execute("ALTER TABLE venue_profiles ADD COLUMN table_configs JSON DEFAULT '[]'")
        conn.commit()
        print("Added column 'table_configs' successfully.")
    except Exception as e:
        print(f"Error adding 'table_configs': {e}")
else:
    print("Column 'table_configs' already exists.")

# Verify columns
cursor.execute("PRAGMA table_info(venue_profiles)")
updated_cols = [row[1] for row in cursor.fetchall()]
print(f"Updated Columns: {updated_cols}")

conn.close()
print("Migration completed!")
