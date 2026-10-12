import sqlite3

from core.const import RECORDS_LIMIT


class DBProxy:
    """Padrao Proxy: o jogo nunca fala com o SQLite diretamente, so com esta classe."""

    def __init__(self, db_name: str):
        self.connection = sqlite3.connect(db_name)
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS records(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                wave INTEGER NOT NULL,
                result TEXT NOT NULL,
                date TEXT NOT NULL)
        ''')

    def save(self, record: dict):
        self.connection.execute(
            'INSERT INTO records (name, score, wave, result, date) VALUES (:name, :score, :wave, :result, :date)',
            record)
        self.connection.commit()

    def retrieve_top(self, limit: int = RECORDS_LIMIT) -> list[tuple]:
        return self.connection.execute(
            'SELECT name, score, wave, result, date FROM records ORDER BY score DESC, id ASC LIMIT ?',
            (limit,)).fetchall()

    def close(self):
        self.connection.close()
