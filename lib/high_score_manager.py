from . import CONN, CURSOR

class Highscore:
    def __init__(self, user, score, id=None):
        self.id = id
        self.user = user
        self.score = score

    def __repr__(self):
        return f"Highscore(user={self.user}, score={self.score})"

    @classmethod
    def create_table(cls):
        sql = """CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY, 
            user_name TEXT, 
            score INTEGER
        )"""
        try:
            CURSOR.execute(sql)
            CONN.commit()
        except Exception as e:
            print(f"An error occurred while creating the table: {e}")

    def add_score(self):
        sql = """INSERT INTO scores (user_name, score) VALUES (?, ?)"""
        try:
            CURSOR.execute(sql, [self.user, self.score])
            CONN.commit()

            last_row_sql = """SELECT * FROM scores ORDER BY id DESC LIMIT 1"""
            self.id = CURSOR.execute(last_row_sql).fetchone()[0]
        except Exception as e:
            print(f"An error occurred while adding score: {e}")
            CONN.rollback()

    @classmethod
    def get_high_scores(cls):
        sql = """SELECT user_name, score FROM scores ORDER BY score DESC LIMIT 5"""
        try:
            sql_return = CURSOR.execute(sql)
            return sql_return.fetchall()
        except Exception as e:
            print(f"An error occurred while retrieving high scores: {e}")
            return []

    @classmethod
    def clean_score_records(cls):
        sql = """DELETE FROM scores WHERE score NOT IN (SELECT score FROM scores ORDER BY score DESC LIMIT 5)"""
        try:
            CURSOR.execute(sql)
            CONN.commit()
        except Exception as e:
            print(f"An error occurred while cleaning score records: {e}")
            CONN.rollback()

    @classmethod
    def initialize_scores(cls, user, score):
        sql = """INSERT INTO scores (user_name, score) VALUES (?, ?)"""
        try:
            CURSOR.execute(sql, [user, score])
            CONN.commit()
        except Exception as e:
            print(f"An error occurred while initializing scores: {e}")
            CONN.rollback()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if isinstance(value, str):
            self._user = value
        else:
            raise TypeError("user value needs to be a string")

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if isinstance(value, int):
            self._score = value
        else:
            raise TypeError("score must be an integer")