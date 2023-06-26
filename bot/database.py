import sqlite3


class Model:
    connection = sqlite3.connect("db.db")
    cursor = connection.cursor()

    def __init__(self, **kwargs):
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS 'users' (
                    'id' INTEGER,
                    'user_id' INTEGER, 
                    'chance' INTEGER,
                    PRIMARY KEY ('id')
                );
            """
        )
        self.kwargs = kwargs

    def perform_assert(self):
        assert "user_id" in self.kwargs.keys() and "chance" in self.kwargs.keys(), ValueError(
            """
                Required values are not specified or set improperly
            """
        )

    def save(self):
        self.perform_assert()
        self.cursor.execute(
            """INSERT INTO users (user_id, chance) VALUES (?, ?)""",
            tuple(self.kwargs.values())
        )
        self.connection.commit()
        return True

    def update(self):
        self.perform_assert()
        self.cursor.execute(
            """UPDATE users SET chance=? WHERE user_id=?;""",
            (self.kwargs['chance'], self.kwargs['user_id'])
        )
        self.connection.commit()
        return True

    def get(self, user_id: int):
        user = self.cursor.execute(
            """SELECT chance FROM users WHERE user_id=?""",
            (user_id,)
        ).fetchall()
        if not user:
            return None
        return user[0][0]

    def get_user(self, user_id):
        user = self.cursor.execute("""SELECT user_id FROM users WHERE user_id=?""", (user_id,)).fetchall()
        if user:
            return user[0][0]
        return None

