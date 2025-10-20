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

def add_column_if_not_exists(table_name, column_name, column_definition):
    """Add a column to an existing table if it doesn't already exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]

            if column_name not in columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
                conn.commit()
                print(f"Added column '{column_name}' to table '{table_name}'")
                return True
            else:
                print(f"Column '{column_name}' already exists in table '{table_name}'")
                return False
        except sqlite3.Error as e:
            print(f"Error adding column: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

# Add a new table for chat history
CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id)
);
"""

def create_tables():
    """Create all necessary database tables if they don't exist, and update schema if needed."""
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

            # Check if we need to add any missing columns to existing tasks table
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [column[1] for column in cursor.fetchall()]

            # Add batch_id column if it doesn't exist (for backward compatibility)
            if 'batch_id' not in columns:
                try:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN batch_id TEXT")
                    print("Added batch_id column to tasks table")
                except sqlite3.Error as e:
                    print(f"Could not add batch_id column: {e}")

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

            # Create chat history table
            cursor.execute(CHAT_HISTORY_TABLE)
            print("SQLite 'chat_history' table checked/created successfully.")

            conn.commit()

        except sqlite3.Error as e:
            print(f"An error occurred while creating tables: {e}")
            conn.rollback()
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

# Ensure the database is initialized when this module is imported
try:
    create_tables()
except Exception as e:
    print(f"An error occurred while initializing the database: {e}")

if __name__ == "__main__":
    print("Initializing database...")
    try:
        create_tables()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
