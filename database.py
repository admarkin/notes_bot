import sqlite3

class Database:
    def __init__(self, user_id):
        self.user_id = user_id

    def create_table(self):
        conn = sqlite3.connect(f'notes_{self.user_id}.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          note TEXT)''')
        conn.commit()
        conn.close()

    def add_note(self, note_text):
        conn = sqlite3.connect(f'notes_{self.user_id}.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (note) VALUES (?)", (note_text,))
        conn.commit()
        conn.close()

    def get_notes(self):
        conn = sqlite3.connect(f'notes_{self.user_id}.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT note FROM notes")
        notes = cursor.fetchall()
        conn.close()
        return notes

