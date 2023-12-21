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

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()