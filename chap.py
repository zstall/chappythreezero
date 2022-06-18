#!/home/ec2-user/venv/python3/bin/python

"""
Author: Zachary Stall
Date: 9/13/2020
Description: The start of chore app. Using a sqlite db, and hopefully a flask,
this application will allow a user to get randomly selected chores assigned to
them daily, weekly, and monthly.

This particular file is a collection of functions to access and update the DB.
"""

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
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
    
        # if no org, add it directory
        if self.org_ids == None:
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + self.user_id + "\"}' WHERE org_id = '" + org_id[0][0] + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + org_id[0][0] + "\"}' where user_id = '" + self.user_id + "';")
            self.org_ids = org_id[0][0]
        # if there are already orgs assigned, check if the org id is already assigned
        elif len(self.org_ids) >= 1 and org_id[0][0] in self.org_ids:
            print("Org Id Already Assigned: " + str(org_id[0][0] in self.org_ids))
        # if multiple orgs are assigned, append the new org
        else:
            print("Appending Org ID to User:")
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + self.user_id + "\"}' WHERE org_id = '" + org_id[0][0] + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + org_id[0][0] + "\"}' where user_id = '" + self.user_id + "';")
            self.org_ids.append(org_id[0][0])

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
            self.user_ids = user_id[0][0]
        elif len(self.user_ids) >= 1 and user_id[0][0] in self.user_ids:
            print("User ID already assigned to org: " + str(user_id[0][0] in self.user_ids))
        else:
            print("Appending User Id to Org:")
            query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + user_id[0][0] + "\"}' where org_id = '" + self.org_id + "';")
            query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + self.org_id + "\"}' where user_id = '" + user_id[0][0] + "';")
            print(self.user_ids)
            self.user_ids.append(user_id[0][0])

def query_chappy(query):
     """ function to connect to the DB and run queries """
     conn = None
     try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
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

def main():



    """    
    the_users = query_chappy("select * from users;")
    
    all_users =[]
    for u in the_users:
        if(u[5] == 'admin'):
            print("are we doing this?")
            all_users.append(create_user(u[5],'admin'))
        else:
            all_users.append(create_user(u[5],'password'))

    
    for u in all_users:
        print(u.username)
    
    """ 
    """
    u = User('','admin','admin', '555-555-5555', 'lstall@noreplay.com','admin', 'admin', '','{}','','True','True','False')
    u.add_user_to_db('admin')
    
    u = create_user("admin", "admin")
    #new_usr.assign_org("kelly_house")
    u.assign_org("stall_house")
    u.assign_org("kelly_house")
    
    
    print("User: " + u.username)
    print(u.org_ids)
    """

    o = Org('', 'BooBoo', '', '{}', False, '')
    o.add_org_to_db()

    o = create_org("BooBoo")

    o.assign_users("zstall")
    o.assign_users("ckelly")
    o.assign_users("zstall")

    print("Org" + o.org_name)
    print(o.user_ids)


if __name__ == '__main__':
    main()