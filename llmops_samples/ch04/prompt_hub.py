import os
import sqlite3

default_database_path = os.path.dirname(os.path.abspath(__file__)) + "/llmops.db"

class PromptHub:
  def __init__(self, database:str = default_database_path):
    self.database = database
    self.init_database()

  def init_database(self):
    conn = sqlite3.connect(self.database)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      prompt_name TEXT NOT NULL UNIQUE,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompt_versions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      prompt_id INTEGER NOT NULL,
      version_id INTEGER NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      system_template TEXT,
      user_template TEXT,
      changed_details TEXT,
      FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
  
  def get_prompt_list(self):
    conn = sqlite3.connect(self.database)
    try:
      cursor = conn.cursor()
      cursor.execute("SELECT prompt_name FROM prompts ORDER BY timestamp DESC")
      rows = cursor.fetchall()
      return [row[0] for row in rows]
    finally:
      conn.close()

  def get_prompt_versions(self, prompt_name:str):
    conn = sqlite3.connect(self.database)
    try:
      cursor = conn.cursor()
      cursor.execute("""
        select pv.version_id, pv.timestamp, pv.system_template, pv.user_template, pv.changed_details
        from prompt_versions pv
        join prompts p on pv.prompt_id = p.id
        where p.prompt_name = ?
        order by pv.timestamp DESC
      """, (prompt_name,))
      rows = cursor.fetchall()
      return rows
    except Exception as e:
      print(f"Error getting prompt versions: {e}")
      return None
    finally:
      conn.close()

  def add_prompt(self, prompt_name:str, system_template:str, user_template:str) -> bool:
    if not prompt_name or not prompt_name.strip():
      return False
    prompt_name = prompt_name.strip().lower().replace(" ", "_")
    conn = sqlite3.connect(self.database)
    try:
      cursor = conn.cursor()
      cursor.execute("""
        INSERT INTO prompts (prompt_name) VALUES (?)
      """, (prompt_name,))

      prompt_id = cursor.lastrowid

      cursor.execute("""
        INSERT INTO prompt_versions (prompt_id, version_id, system_template, user_template, changed_details) VALUES (?, 1, ?, ?, ?)
      """, (prompt_id, system_template, user_template, "init"))

      conn.commit()
      return True
    except Exception as e:
      print(f"Error adding prompt: {e}")
      return False
    finally:
      conn.close()

  def add_prompt_version(self, prompt_name:str, system_template:str, user_template:str, changed_details:str) -> bool:
    if not prompt_name:
      return False
    conn = sqlite3.connect(self.database)
    try:
      cursor = conn.cursor()
      cursor.execute("""
        SELECT id FROM prompts WHERE prompt_name = ?
      """, (prompt_name,))
      result = cursor.fetchone()
      if not result:
        return False
      prompt_id = result[0]

      cursor.execute("""
        SELECT MAX(version_id) FROM prompt_versions WHERE prompt_id = ?
      """, (prompt_id,))
      max_version_result = cursor.fetchone()
      max_version = max_version_result[0] if max_version_result and max_version_result[0] is not None else 0
      new_version_id = max_version + 1

      cursor.execute("""
        INSERT INTO prompt_versions (prompt_id, version_id, system_template, user_template, changed_details) VALUES (?, ?, ?, ?, ?)
      """, (prompt_id, new_version_id, system_template, user_template, changed_details))
      conn.commit()
      return True
    except Exception as e:
      print(f"Error adding prompt version: {e}")
      return False
    finally:
      conn.close()