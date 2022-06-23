import chap
import os
import random
import datetime
from create_chappy_db import executeInserts
from flask import Flask, request, render_template, session, redirect, g,url_for
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
app.secret_key = os.urandom(24)

# This route clears any user info and sets the user and user_id when a user signs in.
@app.before_request
def before_request():
    g.user = None
    g.password = None
    g.user_id = None

    # This is checking if a user is currently logged in, if so set g for user and user_id.
    if 'user' in session:
        g.user = session['user']
        g.user_id = session['user_id']
    
        
# main route def for home directory.        
@app.route("/")
def home():
    return render_template('index.html')

# logout route clears all user info for that session
@app.route("/logout")
def logout():
    # Reset user and user_id
    g.user = None
    g.user_id = None
    # remove user from session
    session.pop('user', None)
    return render_template('index.html')

@app.route("/register", methods=['GET','POST'])
def register():
    #executeInserts(fname, lname, phone, email, username, crypt('password', gen_salt('bf', 8)), "current_timestamp, current_timestamp", admin, "False" )
    return render_template('registration.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)

        usr = chap.create_user(str(request.form['user']), str(request.form['password']))
        
        try:
            session['user'] = usr.username
            session['user_id'] = usr.user_id
            g.user = usr.user_id
            u = usr.user_id
            return redirect(url_for('chores', usr=u))
        except:
            return render_template('login.html')
    return render_template('login.html')

@app.route('/chores/<usr>', methods=['GET', 'POST'])
def chores(usr):

    usr = chap.create_user_with_id(usr)
    usr_id = usr.user_id

    if usr.admin == True:
        completed_chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'True';")
        chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'False';")
        names = chap.query_chappy("select username from users where username <> 'admin' ;")

        chrs = {}
        dchrs = {}
        
        for nm in names:
            chrs[nm[0]]=[]
            dchrs[nm[0]]=[]
        
        for nm in chores:
            chrs[nm[0]]+=[nm[1]]

        for nm in completed_chores:
            dchrs[nm[0]]+=[nm[1]]

        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=usr.username, user_id=usr_id)      

    else:
        completed_chores = chap.query_chappy("SELECT chore FROM chores WHERE user_id = '" + usr.user_id + "' AND done = 'True';")
        chores = chap.query_chappy("SELECT chore FROM chores WHERE user_id = '" + usr.user_id + "' AND done = 'False';")

        chrs = {}
        dchrs = {}

        chrs[usr.fname]=[]
        dchrs[usr.fname]=[]

        for c in chores:
            chrs[usr.fname]+=c
        for c in completed_chores:
            dchrs[usr.fname]+=c
        
        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=usr.username)
    
@app.route("/update", methods=['GET','POST'])
def update_chores():
    if request.method == 'POST':
        chores = (request.form.getlist('chr'))
        for c in chores:
            chr = chap.create_chore(c)
            chr.update_chore()
        usr_id = session.get('user_id', None)

        return redirect(url_for('chores', usr=usr_id))

@app.route("/incomplete", methods=['GET', 'POST'])
def incomplete_chores():
    if request.method == 'POST':
        chores = (request.form.getlist('chr'))
        for c in chores:
            chr = chap.create_chore(c)
            chr.update_chore()
        usr_id = session.get('user_id', None)

        return redirect(url_for('chores', usr=usr_id))

@app.route("/admintools", methods=['GET', 'POST'])
def run_chappy():
    trace = False

    query_org_ids = ("SELECT org_id FROM orgs;")
    org_ids = chap.query_chappy(query_org_ids)
    
    chrs = {}
    wk_chrs = {}
    org_dic = {}

    day = datetime.datetime.today().weekday()

    for org_id in org_ids:
        query_org_users = ("SELECT user_id FROM users WHERE '" + org_id[0] +"' = ANY(org_ids);")
        org_users = chap.query_chappy(query_org_users)

        query_org_chores = ("SELECT chore_id FROM chores WHERE org_id = '" + org_id[0] + "';")
        org_chores = chap.query_chappy(query_org_chores)
        

        while len(org_chores) > 0:
            for user in org_users:
                if org_chores == []:
                    break
                chr_id = org_chores.pop(random.randint(0,len(org_chores)-1))
                update_chore_query_one = ("update chores set user_id = '" + user[0] + "' where chore_id = '" + chr_id[0] + "';")
                chap.query_chappy(update_chore_query_one)
                update_chore_query_two = ("update chores set done = 'False';")
                chap.query_chappy(update_chore_query_two)

    
    
    for i in org_users:
        username = (chap.query_chappy("select username from users where user_id = '" + i[0] + "';"))
        org_name = (chap.query_chappy("select o.org_name from orgs o join chores c on o.org_id = c.org_id where c.user_id = '" + i[0] + "' limit 1;"))
        chore = chap.query_chappy("select chore from chores where user_id = '" + i[0] + "' and schedule_daily = 'True';")
        wk_chr = chap.query_chappy("select chore from chores where user_id = '" + i[0] + "' and schedule_weekly = 'True';")

        org_dic[username[0][0]] = org_name
        chrs[username[0][0]] = chore
        wk_chrs[username[0][0]] = wk_chr

    usr_id = session.get('user_id', None)
    return render_template('resetsuccess.html', users=org_users, chr=chrs, d = day, wchr=wk_chrs, message = chrs, org=org_dic, admin_id = usr_id )

    
if __name__ == '__main__':
    app.run(debug=True)