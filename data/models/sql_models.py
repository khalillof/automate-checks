#!/usr/bin/env python3
import sqlite3


def create_connection(db_path):
    """ create a database connection to the SQLite database
        specified by the db_path
    :param db_file: database file
    :return: Connection object or None
    """

    # connect to db and create cursor
    sqlConnection = sqlite3.connect(db_path)

    return sqlConnection

def get_tables():

    servers_table = """CREATE TABLE IF NOT EXISTS servers (
                                    id integer PRIMARY KEY,
                                    server_name text NOT NULL,
                                    server_os text NOT NULL,
                                    ip_address text NOTt NULL,
                                    total_memory text NOT NULL,
                                    free_memory text NOT NULL,
                                    total_storage text NOT NULL,
                                    free_storage text NOT NULL,
                                    priority integer,
                                    status text NOT NULL,
                                    create_date text NOT NULL,
                                    end_date text NULL,
                                );"""

    websites_table = """CREATE TABLE IF NOT EXISTS websites (
                                    id integer PRIMARY KEY,
                                    website_name text NOT NULL,
                                    website_ip text NULL,
                                    name text NOT NULL,
                                    priority integer,
                                    status integer NOT NULL,                                    
                                    create_date text NOT NULL,
                                    end_date text NULL,
                                    server_id integer NOT NULL,
                                    FOREIGN KEY (server_id) REFERENCES servers (id)
                                );"""

    clients_table = """ CREATE TABLE IF NOT EXISTS clients (
                                        id integer PRIMARY KEY,                                         
                                        client_ip text NOT NULL                                      
                                        status_code NOT NUL,
                                        http_method NOT NULL,                                                                             
                                        attempt interger NOT NULL,
                                        date_time text NOT NULL,
                                        banned integer NOT NULL,
                                        ban_date text  NULL,
                                        release_date text NULL,
                                        ban_reason text NULL,
                                        msg text NULL,
                                        priority integer,
                                        website_id integer NOT NULL,
                                        FOREIGN KEY (website_id) REFERENCES websites (id)
                                    ); """

    return [servers_table, websites_table,clients_table]

def db_execute(cursor, sql_query):

    cursor.execute(sql_query)
    result = cursor.fetchall()
    return result

def create_tables(cursor):

    if cursor:
        for table in get_tables():
            db_execute(cursor, table)
        else:
            print("Error! cannot create the database connection.")

def select_all_tasks(cursor):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    rows = db_execute(cursor, "SELECT * FROM tasks")

    for row in rows:
        print(row)

def select_task_by_priority(cursor, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """

    rows = db_execute(
        cursor, "SELECT * FROM tasks WHERE priority=?", (priority,))

    for row in rows:
        print(row)

def query_db(sql_query,db_path):

    try:
        # Connect to DB and create a cursor
        sqliteConnection = create_connection(db_path)
        cursor = sqliteConnection.cursor()
        print('DB Init')

        # create tables
        #create_tables(cursor)

        query_result=db_execute(cursor,sql_query)
        return query_result;

        # Handle errors
    except sqlite3.Error as err:
        print('Error occured - db query faild ', err)

        # Close DB Connection irrespective of success or failure
    finally:
        # Close the cursor
        if cursor:
            cursor.close()
            print('SQLite cursor closed')

        # close connection
        elif sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')


