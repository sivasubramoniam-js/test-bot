import sqlite3

def create_database():
    conn = sqlite3.connect('insta.db')
    c = conn.cursor()
    
    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT NOT NULL,
            base64_data TEXT NOT NULL,
            response TEXT NOT NULL,
            theme TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
def insert_into_db(file_type, base64_data, theme, response):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO posts (file_type, base64_data, theme, response)
        VALUES (?, ?, ?, ?)
    ''', (file_type, base64_data, theme, response))
    
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    create_database()