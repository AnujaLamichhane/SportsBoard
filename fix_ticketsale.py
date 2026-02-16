import sqlite3


def fix_db():
    db_path = 'db.sqlite3'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Adding transaction_id column to organizer_ticketsale in {db_path}...")

        # We add the column as an integer first to satisfy the OneToOneField relationship
        cursor.execute('''
            ALTER TABLE organizer_ticketsale 
            ADD COLUMN transaction_id INTEGER 
            REFERENCES organizer_khaltitransaction(id) 
            DEFERRABLE INITIALLY DEFERRED;
        ''')

        conn.commit()
        print("Successfully added the column!")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}. (The column might already exist, or the table name is different.)")
    finally:
        conn.close()


if __name__ == "__main__":
    fix_db()