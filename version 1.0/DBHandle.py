import sqlite3

def create_in_db(dbname , sql):
    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()


def create_new_user(user, password):
    DBname= 'GYM.db'
    sql = (f'''INSERT INTO users(username, password) 
    VALUES ({user}, {password})
    ''')
    create_in_db(DBname, sql)


def main():
    conn = sqlite3.connect('GYM.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY
             AUTOINCREMENT,
            username TEXT NOT NULL,
            password INTEGER
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS trainers (
                id INTEGER PRIMARY KEY
                 AUTOINCREMENT,
                id_number INTEGER,
                username TEXT NOT NULL,
                fullname TEXT NOT NULL,
                level TEXT NOT NULL,
                
                
            )
        ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()