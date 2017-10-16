from flask import Flask, request, redirect, render_template, session, flash, session
from mysqlconnection import MySQLConnector
from random import shuffle
import random
import re, md5
import bs4
from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]')
app = Flask(__name__)
app.secret_key = "thisissecret"
mysql = MySQLConnector(app,'reddit')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods = ['post'])
def process():
    input_fname = request.form['first_name']
    input_lname = request.form['last_name']
    input_email = request.form['email']
    input_pass = request.form['pass']
    input_confpass = request.form['conf_pass']

    if(len(input_fname) or len(input_lname) or len(input_email) or len(input_pass) or len(input_confpass)) < 1:
        flash("Field Can not be Empty!!")
        return redirect('/')
    if (len(input_fname) or len(input_lname)) < 2:
        flash("At least needs 2 characters for first name/last name!!")
        return redirect('/')
    if (not NAME_REGEX.match(input_fname)) or (not NAME_REGEX.match(input_lname)):
       flash("First Name/Last Name only contains letters!!")
       return redirect('/')
    if not EMAIL_REGEX.match(input_email):
        flash("Invalid Email Address!")
        return redirect('/')
    else:
        query = "SELECT email FROM users WHERE email = :email"
        data = {
            'email' : input_email
        }
        email_entered = mysql.query_db(query, data)
        if email_entered != []:
            flash("we have this email!!Enter different email id.")
            return redirect('/')
    
    if len(input_pass) < 8:
        flash("Password should be at least 8 characters long!")
        return redirect('/')
    if input_confpass != input_pass:
        flash("Passwords didn't match") 
        return redirect('/')
        
    hashed_pass = md5.new(input_pass).hexdigest()
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :pass , NOW(), NOW())"
    data = {
        'fname' : input_fname,
        'lname' : input_lname,
        'email' : input_email,
        'pass' : hashed_pass
    }
    data_added = mysql.query_db(query, data)
    return redirect('/')
        

@app.route('/login', methods = ['post'])  
def login():
    if 'id' not in session:
        session['id'] = 0
    
    login_email = request.form['login_email']
    login_pass = request.form['login_pass']
    # hashed_pass = md5.new(login_pass).hexdigest()
    if (len(login_email) or len(login_pass)) < 1:
        flash("Field Can not be Empty!!")
        return redirect('/')
    if not EMAIL_REGEX.match(login_email):
        flash("Invalid Email Address!")
        return redirect('/')
    
    if len(login_pass) < 8:
        flash("Password should be at least 8 characters long!")
        return redirect('/')

    else:  
        hashed_pass1 = md5.new(request.form['login_pass']).hexdigest()
        print "hashed pass...{}".format(hashed_pass1)
        query2 = "SELECT user_id,first_name,email,password FROM users WHERE email = :email AND password = :pass"
        data2 = {
            'email' : login_email,
            'pass' : hashed_pass1
            }
        pass_entered = mysql.query_db(query2, data2)
        # session['first'] = pass_entered[0]['first_name']
        
        if pass_entered == []:
            flash("Wrong username or password!!")
            return redirect('/')
        else:
            session['id'] = pass_entered[0]['user_id']
            return redirect ('/admin')

@app.route('/admin_process', methods=['post'])
def admin_process():
    if 'chapter_id' not in session:
        session['chapter_id'] = 0
    
    input_title = request.form['title']
    input_problem = request.form['problem']
    input_chapter = request.form['chapters']
    print  "the select option value:....{}".format(input_chapter)
    query = "SELECT chapter_id FROM chapters WHERE chapter_name = :chapter_name"
    data = {
        'chapter_name' : input_chapter
    }
    get_chapter = mysql.query_db(query,data)
    # query3 = "SELECT titles FROM chapters"
    # get_title = mysql.query_db(query3)
    
    session['chapter_id'] = get_chapter[0]['chapter_id']
    query2 = "INSERT INTO posts (user_id,chapter_id,title,created_at,updated_at,problem) VALUES (:user_id,:chapter_id,:title,NOW(),NOW(),:problem)"
    data2 = {
        'user_id' : session['id'],
        'chapter_id' : session['chapter_id'],
        'title' : input_title,
        'problem' : input_problem
    }
    mysql.query_db(query2,data2)

    return redirect('/admin')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/team', methods = ['post'])
def team():
    # if 'groups' not in session:
    #     session['groups'] = []
    
    query = "SELECT user_id FROM users order by rand() LIMIT 24"
    all_users = mysql.query_db(query)
    random_users = []
    random_list = []
    groups = []
    for user in all_users:
        random_users.append(user['user_id'])
    print random_users
    for i in range(0,len(random_users),3):
        groups.append(random_users[i:i+3])
    print "groups new are!!!!{}".format(groups)
    # for i in range(0,length_group-3,3):
    #     session['groups'].append(random_users[i:i+2])
    
    # print "GROUPS.......{}".format(session['groups'])
    # ---------------------------------
    # random_list = random.sample(range(len(random_users)),1)
    # print random_list
    # print all_users
    
    # print random_users
    # random_list = random.sample(all_users)
    # for user1 in random_users:
    #      random_list.append(random.sample(range(len(random_users)),1))
    # print random_list
    # groups =[random_list[i:i+3] for i in range(0, len(random_list), 3)] 
    # print random_list
    # print random_list[0][0]

    # for i in range(1,(len(random_list)-3)):
    # i = 0
    # while i > len(random_list):
    #     new_list = random_list[i:i+3]
        
    #     i = i+3
    # groups.append(new_list)
    # groups.append(new_list)
        
        # groups.append(random_list[i:i+3])
        # groups.append(random_list[i+1][0])
        # groups.append(random_list[i+2][0])
    # print "Groups are: {}".format(groups)
        
    # random_list = random.sample(range(len(random_users)),3)

    # print random_list
    # random_users = random.randint
    # for i in all_users:
    #     query = "SELECT user_id FROM users order by rand() LIMIT 3"

    return redirect('/admin')

@app.route('/dashboard')
def dashboard():
    query = "SELECT title,DATE_FORMAT(created_at, '%M %D %Y %H:%i') AS created_at from posts ORDER BY created_at DESC"
    posts = mysql.query_db(query)
    return render_template('dashboard.html', posts = posts)


@app.route('/problem')
def problem():
    data = "<li id='post_list'><a href='/problem' valueid='post_links'>{{post['title']}}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{post['created_at']}}</a></li>"
    soup = BeautifulSoup(data)
    print soup.find('a').contents[0]
    
    query = "SELECT title,problem from posts WHERE chapter_id = {}".format(session['chapter_id'])
    problem = mysql.query_db(query)
    return render_template('problem.html', problem = problem)
app.run(debug=True)