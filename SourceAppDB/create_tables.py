import psycopg2
from queries import drop_table_logs, create_table_logs
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import configparser

config = configparser.ConfigParser()
config.read('config-correct.ini')
username = config["POSTGRES"]["user"]
password = config["POSTGRES"]["pass"]


def create_database():
    print(username, password)
    conn = psycopg2.connect(f"host=127.0.0.1 user={username} password={password}")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS user_logs")
    cur.execute("CREATE DATABASE user_logs")

    conn.close()

    conn = psycopg2.connect(f"host=127.0.0.1 dbname=user_logs user={username} password={password}")
    cur = conn.cursor()

    return conn, cur


def delete_tables(conn, cur):
    cur.execute(drop_table_logs)
    conn.commit()


def create_tables(conn, cur):
    cur.execute(create_table_logs)
    conn.commit()


def main():
    conn, cur = create_database()

    delete_tables(conn, cur)
    print("Tables deletes successfully!")

    create_tables(conn, cur)
    print("Tables created successfully!")

    conn.commit()
    print("Inserted Values Properly")

    conn.close()


if __name__ == "__main__":
    main()
