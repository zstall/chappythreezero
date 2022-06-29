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
    if request.method == 'POST':
            
        # Create a new user and add them to the DB to generate user_id and crypt password

        admin = (request.form['admin'].lower() == 'y')

        u = chap.User('',str(request.form['fname']),str(request.form['lname']),str(request.form['phone']),str(request.form['email']),str(request.form['username']),str(request.form['password']),'{}','','',str(admin),'False','False')
        u.add_user_to_db(u.password)
        u = chap.create_user(u.username, u.password)
        o = "None"

        if len(str(request.form['org_name'])) > 0:
            o = chap.Org('',str(request.form['org_name']),'','{}','False','')
            o.add_org_to_db()
            o = chap.create_org(o.org_name)
            o.assign_users(u.username)
            u.assign_org(o.org_name)

            o = chap.create_org(o.org_name)
            u = chap.create_user_with_id(u.user_id)

        elif len(str(request.form['org_id'])) > 0:
            o = chap.create_org_with_id(str(request.form['org_id']))
            o.assign_users(u.username)
            u.assign_org(o.org_name)



        return render_template('successfulReg.html', o=o, u=u)
        

    
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

        completed_chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'True' and '"+str(usr.org_ids[0])+"' = ANY(u.org_ids);")
        chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'False' and '"+str(usr.org_ids[0])+"' = ANY(u.org_ids);")
        names = chap.query_chappy("select username from users where username <> 'admin' and '"+str(usr.org_ids[0])+"' = ANY(org_ids);")
        orgs = usr.org_ids

        chrs = {}
        dchrs = {}
        dorgs = {}

    
        for nm in names:
            chrs[nm[0]]=[]
            dchrs[nm[0]]=[]
        

        for nm in chores:
            chrs[nm[0]]+=[nm[1]]
            dorgs[nm[1]]=orgs
        

        #chrs={c:chrs[c] for c in chrs if chrs[c]}

        for nm in completed_chores:
            dchrs[nm[0]]+=[nm[1]]

        #dchrs={c:dchrs[c] for c in dchrs if dchrs[c]}  

        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=usr.username, user_id=usr_id, u=usr, o=dorgs)      

    elif usr.super_user == True:
        completed_chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'True';")
        chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'False';")
        names = chap.query_chappy("select username from users where username <> 'admin';")
        orgs = chap.query_chappy("select c.chore, c.org_id from users u join chores c on u.user_id::varchar = c.user_id;")

        chrs = {}
        dchrs = {}
        dorgs = {}
        
        for nm in names:
            chrs[nm[0]]=[]
            dchrs[nm[0]]=[]
        
        for c in orgs:
            dorgs[c[0]]=[c[1]]
        
        for nm in chores:
            chrs[nm[0]]+=[nm[1]]

        #chrs={c:chrs[c] for c in chrs if chrs[c]}

        for nm in completed_chores:
            dchrs[nm[0]]+=[nm[1]]

        #dchrs={c:dchrs[c] for c in dchrs if dchrs[c]}  


        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=usr.username, user_id=usr_id, u=usr, o=dorgs)      

    else:
        completed_chores = chap.query_chappy("SELECT chore FROM chores WHERE user_id = '" + usr.user_id + "' AND done = 'True';")
        chores = chap.query_chappy("SELECT chore FROM chores WHERE user_id = '" + usr.user_id + "' AND done = 'False';")
        orgs = chap.query_chappy("select c.chore, c.org_id from users u join chores c on u.user_id::varchar = c.user_id where u.user_id = '"+usr.user_id+"';")

        chrs = {}
        dchrs = {}
        dorgs = {}

        chrs[usr.fname]=[]
        dchrs[usr.fname]=[]

        for c in chores:
            chrs[usr.fname]+=c
        for c in completed_chores:
            dchrs[usr.fname]+=c
        for c in orgs:
            dorgs[c[0]]=usr.org_ids


        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=usr.username, user_id=usr_id, u=usr, o=dorgs)
    
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