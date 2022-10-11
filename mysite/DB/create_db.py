import sqlite3
from queries import *


def create_db():
    conn = sqlite3.connect("./target_db.db")
    curr = conn.cursor()

    curr.execute(drop_table_logs)
    curr.execute(create_table_logs)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
