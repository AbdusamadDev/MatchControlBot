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
        assert "user_id" in self.kwargs.keys() and "chance" in self.kwargs.values(), ValueError(
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
            """UPDATE table_name SET chance=? WHERE user_id=?;""",
            tuple(self.kwargs.values())
        )
        self.connection.commit()
        return True

    def get(self, user_id: int):
        user = self.cursor.execute("""SELECT user_id, chance WHERE user_id=?""", (user_id,)).fetchall()[0]
        return user


if __name__ == '__main__':
    m = Model(user_id=55, chance=88)
    # print(tuple(m.kwargs))
    print(m.save())
