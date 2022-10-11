
drop_table_logs = "DROP TABLE IF EXISTS users"

create_table_logs = '''CREATE TABLE IF NOT EXISTS users(
                       email VARCHAR, name VARCHAR, 
                       surname VARCHAR, password VARCHAR
                        )
                    '''