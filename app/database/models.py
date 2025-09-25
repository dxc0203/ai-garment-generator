# File: app/database/models.py
import sqlite3

DATABASE_NAME = "data/main.db"

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables():
    """Create all necessary database tables if they don't exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # --- tasks table with new 'batch_id' column ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT,
                status TEXT NOT NULL DEFAULT 'NEW',
                uploaded_image_paths TEXT,
                spec_sheet_text TEXT,
                final_prompt TEXT,
                generated_image_path TEXT,
                redo_prompt TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                product_name TEXT,
                product_tags TEXT,
                batch_id TEXT
            );
            """)
            print("SQLite 'tasks' table checked/created successfully.")
            
            # --- spec_sheet_versions table ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS spec_sheet_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                spec_text TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            );
            """)
            print("SQLite 'spec_sheet_versions' table checked/created successfully.")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                step_name TEXT,
                user_input TEXT,
                ai_prompt TEXT,
                ai_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            );
            """)
            print("SQLite 'interactions' table checked/created successfully.")

            
        except sqlite3.Error as e:
            print(f"An error occurred while creating tables: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    # To apply this change, delete the old main.db file and run this script.
    create_tables()
