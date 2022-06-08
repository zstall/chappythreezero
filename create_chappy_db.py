#!/usr/bin/python
import psycopg2
import os
from config import config

def executeScript(script):
    """" Fill out laters, yes I'm lazy :) """

    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        
        # execute script
        print("Execute Script " + str(script))

        os.system("psql -U admin -d chappy -a -f " + query)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            print('Queries Executed Succesfully.') 

def executeInserts(fn, ln, ph, eml, usrnm, psswrd, created, usr_admin, usr_super_user):
    """" Fill out laters, yes I'm lazy :) """

    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        query = "INSERT INTO users (fname, lname, phone, email, username, password, date_created, user_admin, user_super_user) VALUES("+fn+","+ln+","+ph+","+eml+","+usrnm+","+psswrd+","+created+","+usr_admin+","+usr_super_user+");"

        # create a cursor
        cur = conn.cursor()
        print('Executing query:')
        print(query)
        cur.execute(query)
        conn.commit()

        db_query = cur.fetchone()
        print(db_query)

         # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            print('Queries Executed Succesfully.')

def connect(query="SELECT version();",script=False):
    """ function to connect to the DB and run scripts or queries """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        
        # execute statement
        if(not script):
            print('Executing query:')
            print(query)
            cur.execute(query)

            conn.commit()
            db_query = cur.fetchone()
            print(db_query)
        else:
            print("Execute Script")
            os.system("psql -U admin -d chappy -a -f " + query)

    # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            print('Queries Executed Succesfully.')    


def main():

    # use chappy_tables.sql to create tables for chappy
    connect()
    print()
    print()
    connect('"chappy_tables.sql"', True)
    print()
    print()
    executeInserts("'admin'", "'admin'", "'5555555555'", "'admin@noreply.com'", "'admin'", "crypt('admin', gen_salt('bf', 8))","current_timestamp", "True", "True")
    executeInserts("'Zach'", "'Stall'", "'5555555555'", "'zstall@noreply.com'", "'zstall'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "True", "False")
    executeInserts("'Sam'", "'Stall'", "'5555555555'", "'sstall@noreply.com'", "'sstall'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "False", "False")
    executeInserts("'Caitlin'", "'Kelly'", "'5555555555'", "'ckelly@noreply.com'", "'ckelly'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "False", "False")
    executeInserts("'Test'", "'User'", "'5555555555'", "'tuser@noreply.com'", "'tuser'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "False", "False")

if __name__ == '__main__':
    main()

