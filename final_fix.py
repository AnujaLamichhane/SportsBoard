import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'db.sqlite3')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the KhaltiTransaction table manually
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizer_khaltitransaction (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        pidx varchar(255) NOT NULL,
        amount decimal NOT NULL,
        status varchar(20) NOT NULL,
        purchase_order_id varchar(255) NOT NULL,
        created_at datetime NOT NULL,
        user_id integer NOT NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED
    );
    """)

    conn.commit()
    print("Successfully created organizer_khaltitransaction!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()