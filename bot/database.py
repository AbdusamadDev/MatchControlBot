import sqlite3


class Model:
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()

    def __init__(self, **kwargs):
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS 'users' (
                    'user_id' INTEGER, 
                    'username' TEXT, 
                    'date' TEXT, 
                    'full_name' TEXT, 
                    'phone_number' TEXT, 
                    'region' TEXT
                );
            """
        )

    def save(self):
        pass
