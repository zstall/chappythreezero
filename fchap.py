import chap
import os
import datetime
from flask import Flask, request, render_template, session, redirect, g,url_for
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
app.secret_key = os.urandom(24)

@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)

        usr = chap.create_user(str(request.form['user']), str(request.form['password']))

        if usr != 'Incorrect username or password':
            session['user'] = usr.username
            u = usr.user_id
            return redirect(url_for('chores', u=u))
    
    return render_template('login.html')

@app.route('/chores/<u>', methods=['GET', 'POST'])
def chores(u):

    usr = chap.create_user_with_id(u)

    if usr.username == 'admin':
        completed_chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'True';")
        chores = chap.query_chappy("select u.username, c.chore from users u join chores c on u.user_id::varchar = c.user_id where c.done = 'False';")
        names = chap.query_chappy("select username from users where username <> 'admin';")

        chrs = {}
        dchrs = {}

        for nm in names:
            chrs[nm[0]]=[]
            dchrs[nm[0]]=[]
        
        for nm in chores:
            chrs[nm[0]]+=[nm[1]]

        for nm in completed_chores:
            dchrs[nm[0]]+=[nm[1]]

        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=usr.username)      

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
        
        return render_template('chores.html', chrs=chrs, dchrs=dchrs, user=session['user'])
    


if __name__ == '__main__':
    app.run(debug=True)