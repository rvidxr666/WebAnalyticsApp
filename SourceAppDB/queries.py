
drop_table_logs = "DROP TABLE IF EXISTS logs"

create_table_logs = '''CREATE TABLE IF NOT EXISTS logs(
                       username VARCHAR, user_id INT NOT NULL, 
                       name VARCHAR, surname VARCHAR, 
                       gender VARCHAR, method VARCHAR, 
                       route VARCHAR, status VARCHAR, 
                       time TIME,
                       date DATE
                        )
                    '''