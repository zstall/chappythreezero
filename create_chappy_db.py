#!/usr/bin/python
import psycopg2
import os
from config import config

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
            cur.execute(query)

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
    #connect()
    connect('"chappy_tables.sql"', True)



if __name__ == '__main__':
    main()

