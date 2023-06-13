#!/home/ubuntu/chappythreezero/chp/bin/python3
import psycopg2
import os
from chap import Org, Chore, User, create_user, create_org
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

def executeInserts(fn, ln, ph, eml, usrnm, psswrd, created, updated, usr_admin, usr_super_user):
    """" Fill out laters, yes I'm lazy :) """

    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        query = "INSERT INTO users (fname, lname, phone, email, username, password, date_created, date_updated, user_admin, user_super_user) VALUES("+fn+","+ln+","+ph+","+eml+","+usrnm+","+psswrd+","+created+","+updated+","+usr_admin+","+usr_super_user+");"

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


    users=[
        ["admin", "admin", "5555555555", "admin@noreply.com", "admin", "admin","current_timestamp","current_timestamp", "True", "True"],
        ["admin2", "admin2", "5555555555", "tester1@noreply.com", "admin2", "admin","current_timestamp","current_timestamp", "True", "False"],
        ["test1", "tester1", "5555555555", "tester1@noreply.com", "tester1", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test2", "tester2", "5555555555", "tester1@noreply.com", "tester2", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test3", "tester3", "5555555555", "tester1@noreply.com", "tester3", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test4", "tester4", "5555555555", "tester1@noreply.com", "tester4", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test5", "tester5", "5555555555", "tester1@noreply.com", "tester5", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test6", "tester6", "5555555555", "tester1@noreply.com", "tester6", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test7", "tester7", "5555555555", "tester1@noreply.com", "tester7", "password","current_timestamp","current_timestamp", "True", "False"],
        ["test8", "tester8", "5555555555", "tester1@noreply.com", "tester8", "password","current_timestamp","current_timestamp", "True", "False"]
    ]

    orgs=[
        ['', 'datadogOne', '', '{}', False, ''],
        ['', 'datadogTwo', '', '{}', False, '']
    ]

    daily_chores=['clean kitchen', 'clean living room', 'clean upstairs', 'clean bathroom', 'dishes', 'clean basement', 'dinner', 'drop off maggie', 'pick up maggie']
    weekly_chores = ['cut grass', 'vacuum', 'laundry', 'clean fridge', 'wash cars', 'get groceries']


    user_objects = []
    org_objects  = []


    for i in users:
        u = User('',i[0],i[1],i[2],i[3],i[4],i[5],'{}',i[6],i[7],i[8],i[9],'False') 
        u.add_user_to_db(u.password)
        u_with_id = create_user(u.username, u.password)
        user_objects.append(u_with_id)


    o1 = Org(orgs[0][0], orgs[0][1], orgs[0][2], orgs[0][3], orgs[0][4], orgs[0][5])
    o2 = Org(orgs[1][0], orgs[1][1], orgs[1][2], orgs[1][3], orgs[1][4], orgs[1][5])
    
    o1.add_org_to_db()
    o2.add_org_to_db()

    o1=create_org('datadogOne')
    o2=create_org('datadogTwo')

    o1.assign_users('admin')
    o2.assign_users('admin')

    user_objects.remove(user_objects[0])
        
    for i in range(0, len(user_objects)):
        if i % 2:
            o1.assign_users(user_objects[i].username)
        else:
            o2.assign_users(user_objects[i].username)

    for ch in daily_chores:
        c = Chore('',ch,'True', 'False','','','','','','False')
        c.add_chore_to_db('datadogOne')

    for ch in weekly_chores:
        c = Chore('',ch,'False', 'True','','','','','', 'False')
        c.add_chore_to_db('datadogOne')

    for ch in daily_chores:
        c = Chore('',ch,'True', 'False','','','','','','False')
        c.add_chore_to_db('datadogTwo')

    for ch in weekly_chores:
        c = Chore('',ch,'False', 'True','','','','','', 'False')
        c.add_chore_to_db('datadogTwo')


'''
    # use chappy_tables.sql to create tables for chappy
    connect()
    print()
    print()
    connect('"chappy_tables.sql"', True)
    print()
    print()
    executeInserts("'admin'", "'admin'", "'5555555555'", "'admin@noreply.com'", "'admin'", "crypt('admin', gen_salt('bf', 8))","current_timestamp","current_timestamp", "True", "True")
    executeInserts("'test1'", "'tester1'", "'5555555555'", "'tester1@noreply.com'", "'tester1'", "crypt('password', gen_salt('bf', 8))","current_timestamp","current_timestamp", "True", "False")
    executeInserts("'test2'", "'tester2'", "'5555555555'", "'tester2@noreply.com'", "'tester2'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "current_timestamp","False", "False")
    executeInserts("'tester3'", "'tester3'", "'5555555555'", "'tester3@noreply.com'", "'tetser3'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "current_timestamp","False", "False")
    executeInserts("'tester4'", "'tester4'", "'5555555555'", "'tester4@noreply.com'", "'tester4'", "crypt('password', gen_salt('bf', 8))","current_timestamp", "current_timestamp", "False", "False")
'''
if __name__ == '__main__':
    main()

