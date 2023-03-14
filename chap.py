#!/home/ec2-user/venv/python3/bin/python

"""
Author: Zachary Stall
Date: 9/13/2020
Description: The start of chore app. Using a sqlite db, and hopefully a flask,
this application will allow a user to get randomly selected chores assigned to
them daily, weekly, and monthly.
Testing Github Webhook number 2.
This particular file is a collection of functions to access and update the DB.
"""

# Download the helper library from https://www.twilio.com/docs/python/install
#from logging.config import _OptionalDictConfigArgs
#from urllib.parse import quote_from_bytes
#from twilio.rest import Client
import csv
import datetime
import random
import sys
import psycopg2
import os
from config import config
from create_chappy_db import executeInserts


class User:
    """ Class User is the main class to create a user and update the DB"""
    def __init__(self, user_id, fname, lname, phone, email, username, password, org_ids, date_created, date_updated, admin, super_user, deleted):
        self.user_id = user_id
        self.fname = fname
        self.lname = lname
        self.phone = phone
        self.email = email
        self.username = username  
        self.password = password
        self.org_ids = org_ids
        self.date_created = date_created
        self.date_updated = date_updated 
        self.admin = admin
        self.super_user = super_user
        self.deleted = deleted
    
    def add_user_to_db(self, psswrd):
        query = "INSERT INTO users (fname, lname, phone, email, username, org_ids, password, date_created, date_updated, user_admin, user_super_user) VALUES(" + "'"+self.fname+"', " + "'"+self.lname+"' ," + "'"+self.phone+"' ," + "'"+self.email+"', " + "'"+self.username+"' , '" + self.org_ids + "', " + "crypt('"+psswrd+"', gen_salt('bf', 8)), current_timestamp, current_timestamp, " + self.admin + "," + self.super_user +");"
        query_chappy(query)
    
    def assign_org(self, org):
        """ 
            Assign an org attribute to a user.
            Org must already exist in the DB.
            Orgs in the DB already assigned will be ignored.  
        """
        # get the unique org from the db
        org_id = query_chappy("SELECT org_id FROM orgs WHERE org_name = '" + org + "';")
        print(org_id)
        # if no org, add it directly
        if self.org_ids == None:
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + self.user_id + "\"}' WHERE org_id = '" + org_id[0][0] + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + org_id[0][0] + "\"}' where user_id = '" + self.user_id + "';")
            query_chappy("UPDATE users SET date_updated = current_timestamp WHERE user_id = '" + self.user_id + "';")
            query_chappy("UPDATE orgs SET date_updated = current_timestamp WHERE org_id = '" + org_id[0][0] + "';")
            self.org_ids = org_id[0][0]
        # if there are already orgs assigned, check if the org id is already assigned
        elif len(self.org_ids) >= 1 and org_id[0][0] in self.org_ids:
            print("Org Id Already Assigned: " + str(org_id[0][0] in self.org_ids))
        # if multiple orgs are assigned, append the new org
        else:
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + self.user_id + "\"}' WHERE org_id = '" + org_id[0][0] + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + org_id[0][0] + "\"}' where user_id = '" + self.user_id + "';")
            query_chappy("UPDATE users SET date_updated = current_timestamp WHERE user_id = '" + self.user_id + "';")
            query_chappy("UPDATE orgs SET date_updated = current_timestamp WHERE org_id = '" + org_id[0][0] + "';")
            self.org_ids+= (", " + (org_id[0][0]))

class Org:
    def __init__(self, org_id, org_name, date_created, user_ids, org_deleted, date_udpated):
        self.org_id = org_id
        self.org_name = org_name 
        self.date_created = date_created
        self.user_ids = user_ids
        self.org_deleted = org_deleted
        self.date_updated = date_udpated

    def add_org_to_db(self):
        query = "INSERT INTO orgs (org_name, date_created, user_ids, org_deleted, date_updated) VALUES(" + "'"+self.org_name+"', " + "current_timestamp, '" + self.user_ids +"', 'False', current_timestamp);"
        query_chappy(query)

    def assign_users(self, user_name):
        user_id = query_chappy("SELECT user_id FROM users WHERE username = '" + user_name +"';")

        if self.user_ids == None:
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + user_id[0][0] + "\"}' where org_id = '" + self.org_id + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + self.org_id + "\"}' where user_id = '" + user_id[0][0] + "';")
            query_chappy("UPDATE users SET date_updated = current_timestamp WHERE user_id = '" + user_id[0][0] + "';")
            query_chappy("UPDATE orgs SET date_updated = current_timestamp WHERE org_id = '" + self.org_id + "';")
            self.user_ids = user_id[0][0]
        elif len(self.user_ids) >= 1 and user_id[0][0] in self.user_ids:
            print("User ID already assigned to org: " + str(user_id[0][0] in self.user_ids))
        else:
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + user_id[0][0] + "\"}' where org_id = '" + self.org_id + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + self.org_id + "\"}' where user_id = '" + user_id[0][0] + "';")
            query_chappy("UPDATE users SET date_updated = current_timestamp WHERE user_id = '" + user_id[0][0] + "';")
            query_chappy("UPDATE orgs SET date_updated = current_timestamp WHERE org_id = '" + self.org_id + "';")
            self.user_ids+= (", " + (user_id[0][0]))

class Chore:
    def __init__(self, chore_id, chore, schedule_daily, schedule_weekly, user_id, org_id, chore_deleted, date_created, date_updated, done):
        self.chore_id = chore_id
        self.chore = chore
        self.schedule_daily = schedule_daily
        self.schedule_weekly = schedule_weekly
        self.user_id = user_id
        self.org_id = org_id
        self.chore_deleted = chore_deleted
        self.done = done

    def add_chore_to_db(self,org_name):
        org_id_array = query_chappy("SELECT org_id FROM orgs WHERE org_name = '"+ org_name+"';")
        print(org_id_array)
        org_id = org_id_array[0][0]
        self.org_id = org_id
        query = "INSERT INTO chores (chore, schedule_daily, schedule_weekly, org_id, date_created, date_updated, done) VALUES("+"'"+self.chore+"', '"+self.schedule_daily+"', '"+self.schedule_weekly+"', '"+self.org_id+"', current_timestamp, current_timestamp, 'False');"
        query_chappy(query)

    def add_user_to_chore(self, user_name):
        user_id_array = query_chappy("SELECT user_id FROM users WHERE username = '"+user_name+"';")
        user_id = user_id_array[0][0]
        self.user_id = user_id
        query = "UPDATE chores SET user_id = '"+self.user_id+"' WHERE chore_id = '" +self.chore_id+"';"
        query_chappy(query)

    def add_user_to_chore_user_id(self, user_id):
        self.user_id = user_id
        query = "UPDATE chores SET user_id = '"+self.user_id+"' WHERE chore_id = '" +self.chore_id+"';"
        query_chappy(query)

    def update_chore(self):
        self.done = not(self.done)
        query = "UPDATE chores set done = '" + str(self.done) + "' WHERE chore_id = '" + self.chore_id + "';"
        query_chappy(query)

def query_chappy(query, trace=False):
     """ function to connect to the DB and run queries """
     conn = None
     try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        if trace:
            print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        if trace:
            print("******************************")
            print("Executing:")
            print(query)
            print("******************************")
        cur.execute(query)
        conn.commit()
        
        db_query = cur.fetchall()
        return(db_query) 
        
     except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
     finally:
        if conn is not None:
            cur.close()
            conn.close()

def check_user_password(username, password):
    u = query_chappy("select * from users where username = '" + username + "' and password = crypt('" +password +"',password);")

    if u == '':
        print("Incorrect username or password")
        return False
    elif u == []:
        print("Incorrect username or password")
        return False
    else:
        return True


def create_user(username, password):
    """ Given a username and password query the db to see if that user exists. If so 
        create a user"""
    u = query_chappy("select * from users where username = '" + username + "' and password = crypt('" +password +"',password);")

    if u == '':
        print("Incorrect username or password")
        pass
    elif u == []:
        print("Incorrect username or password")
        pass
    else:
        created_user = User(u[0][0],u[0][1],u[0][2],u[0][3],u[0][4],u[0][5],u[0][6],u[0][7],u[0][8],u[0][9],u[0][10],u[0][11],u[0][12])
        return created_user

def create_user_with_id(id):

    u = query_chappy("select * from users where user_id = '" + id +"';")    
    new_user = User(u[0][0],u[0][1],u[0][2],u[0][3],u[0][4],u[0][5],u[0][6],u[0][7],u[0][8],u[0][9],u[0][10],u[0][11],u[0][12])
    return new_user

def create_org(org_name):
    o = query_chappy("select * from orgs where org_name = '" + org_name + "';")
    if o == '':
        print("Incorrect org name")
        pass
    elif o == []:
        print("Incorrect org name")
        pass
    else:
        create_org = Org(o[0][0],o[0][1],o[0][2],o[0][3],o[0][4],o[0][5])
        return create_org

def create_org_with_id(org_id):
    o = query_chappy("select * from orgs where org_id = '" + org_id + "';")
    if o == '':
        print("Incorrect org name")
        pass
    elif o == []:
        print("Incorrect org name")
        pass
    else:
        create_org = Org(o[0][0],o[0][1],o[0][2],o[0][3],o[0][4],o[0][5])
        return create_org

def create_chore(chore_name):
    chore = chore_name.lower()
    c = query_chappy("select * from chores where chore = '" + chore + "';")
    if c == '':
        print("Chore does not exist")
        pass
    elif c == []:
        print("Chore does not exist")
        pass
    else:
        create_chore = Chore(c[0][0],c[0][1],c[0][2],c[0][3],c[0][4],c[0][5],c[0][6],c[0][7],c[0][8],c[0][9])
        print(create_chore.chore, file=sys.stderr)
        return create_chore

def create_chore_with_user_name(chore_name, user_name):
    chore = chore_name.lower()
    user_id = query_chappy("select user_id from users where username = '" + user_name + "';")
    c = query_chappy("select * from chores where chore = '" + chore + "' and user_id = '" + user_id[0][0] +"';")
    if c == '':
        print("Chore does not exist")
        pass
    elif c == []:
        print("Chore does not exist")
        pass
    else:
        create_chore = Chore(c[0][0],c[0][1],c[0][2],c[0][3],c[0][4],c[0][5],c[0][6],c[0][7],c[0][8],c[0][9])
        return create_chore


def main():

    trace_user = False
    trace = True

    if trace:
        print("Select from an option below: ")
        print("[1] to add a user in the console")
        print("[2] Add org in the console")
        print("[3] Add chores in the console")
        print("[4] Set up a single org with chores")
        print("[5] Debugging Chore Problem")

        num = input("Enter a number: ")

    if trace_user:    
        the_users = query_chappy("select * from users;")
        
        all_users =[]
        for u in the_users:
            if(u[5] == 'admin'):
                all_users.append(create_user(u[5],'admin'))
            else:
                all_users.append(create_user(u[5],'password'))

        
        for u in all_users:
            print(u.username)
    
    # Testing the user class


    if trace and num == '5':
        
        query_org_users = ("SELECT user_id FROM users WHERE 'fd268497-0bea-4d04-bd8d-11669d6bf027' = ANY(org_ids);")
        lst = query_chappy(query_org_users)
        print(lst)
        lst.remove(('0a7c6286-fcab-4e19-a7a9-c5c24e926a2c',))
        print(lst)

    if trace and num == '1':
        print("Add a new user")
        fname = input("Enter First Name: ")
        lname = input("Enter Last Name: ")
        phone = input("Enter Phone Number: ")
        email = input("Enter Email: ")
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        admin = (input("Admin y or n: ")).lower
        super_user = (input("Super User y or n: ")).lower
        org_name = input("Optional: Enter Org Name: ")

        # Create a new user and add them to the DB to generate user_id and crypt password
        u = User('',fname,lname, phone, email, username, password,'{}','', '', str((admin == 'y')),str((super_user == 'y')),'False')
        u.add_user_to_db(password)

        # Create a new instance of User with the user_id and crypted password
        u = create_user(username, password)

        # If an org, assign it here
        if len(org_name) > 0:
            u.assign_org(org_name) 
        
        print("User: " + u.username)
        print("id" + u.user_id)
        if len(org_name) > 0:
            print(u.org_ids)
    

    elif trace and num == '2':
        org_n = input("Enter Org Name: ")
        num = int(input("Optional: How many users would you like to add to the org: "))
        usr = []

        while len(usr) < num:
            u = input("Enter Username: ")
            print(str(num - 1) + " Users left to add ")
            usr.append(u)    

        # Create a new org:
        o = Org('', org_n, '', '{}', False, '')
        # Add the org to the db to generate org id and timestamps
        o.add_org_to_db()

        # Re-create the instance of org with it's id and timestamps
        o = create_org(org_n)

        for u in usr:
            o.assign_users(u)
        

        print("Org: " + o.org_name)
        print("Org Id: " + o.org_id)
        print("Assigned users: ")
        
        o = create_org(org_n)
        print(o.user_ids)

        
    elif trace and num == '3':
        
        chore_nm = input("Enter Chore name: ")
        org_name = input("Enter Org Name: ")
        day = input("Is the chore daily [y] or [n] (Note, if the chore is not daily it will be added to weekly): ")


        # get local instance of the chore
        c = Chore('',chore_nm,str(day.lower()=='y'),str(day.lower()!='y'),'','','','','')
        
        # add the local instance to the db to generate other fields
        c.add_chore_to_db(org_name)
        
        # Recreate instance with auto generated fields
        c = create_chore(c.chore)

        print("The outputs: ")
        print(c.chore)
        print(c.org_id)
        print(c.schedule_weekly)
        print(c.schedule_daily)
    
    elif trace and num == '4':

        org = input('Please enter an Org Name: ')

        o = Org('', org, '', '{}', False, '')
        o.add_org_to_db()
        o = create_org(org)

        add_test_chores = (input("Would you like to add test chores? [y]/[n]: ")).lower()
        if add_test_chores == 'y':
              
            daily_chores = ['clean kitchen', 'clean living room', 'clean upstairs', 'clean bathroom', 'dishes', 'clean basement', 'dinner', 'drop off maggie', 'pick up maggie']
            weekly_chores = ['cut grass', 'vacuum', 'laundry', 'clean fridge', 'wash cars', 'get groceries']
        
            for ch in daily_chores:
                c = Chore('',ch,'True', 'False','','','','','','False')
                c.add_chore_to_db(org)

            for ch in weekly_chores:
                c = Chore('',ch,'False', 'True','','','','','', 'False')
                c.add_chore_to_db(org)
        

        query_org_id = ("SELECT org_id FROM orgs WHERE org_name = '" + org +"';")
        org_id = query_chappy(query_org_id)
        print(org_id[0][0])
        query_org_users = ("SELECT user_id FROM users WHERE '" + org_id[0][0] +"' = ANY(org_ids);")
        org_users = query_chappy(query_org_users)

        query_org_chores = ("SELECT chore_id FROM chores WHERE org_id = '" + org_id[0][0] + "';")
        org_chores = query_chappy(query_org_chores)

        print(org_users)
        print(org_chores)

        while len(org_chores) > 0:
            for user in org_users:
                if org_chores == []:
                    break
                chr_id = org_chores.pop(random.randint(0,len(org_chores)-1))
                update_chore_query = ("update chores set user_id = '" + user[0] + "' where chore_id = '" + chr_id[0] + "';")
                query_chappy(update_chore_query)

if __name__ == '__main__':
    main()
