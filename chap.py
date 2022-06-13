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


class User:

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
    


    def assign_org(self, org):
        org_id = query_chappy("SELECT org_id FROM orgs WHERE org_name = '" + org + "';")
        query_chappy("UPDATE orgs SET user_ids = user_ids || '{\"" + self.user_id + "\"}' WHERE org_id = '" + org_id[0][0] + "';")
        query_chappy("UPDATE users SET org_ids = org_ids || '{\"" + org_id[0][0] + "\"}' where user_id = '" + self.user_id + "';")
        self_org_ids = org_

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

        print(query)
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
            print('Database connection closed.')
            print('Queries Executed Succesfully.')

def create_user(username, password):
    """ Given a username and password query the db to see if that user exists. If so 
        create a user"""
    u = query_chappy("select * from users where username = '" + username + "' and password = crypt('" +password +"',password);")
    
    if u == '':
        return ("Incorrect username or password")
    else:
        aman = User(u[0][0],u[0][1],u[0][2],u[0][3],u[0][4],u[0][5],u[0][6],u[0][7],u[0][8],u[0][9],u[0][10],u[0][11],u[0][12])
        return aman

def main():

    u = create_user("sstall", "password")
    u.assign_org("stall_house")

    print("User: " + u.username)
    print("Org: " + u.org_ids)
if __name__ == '__main__':
    main()