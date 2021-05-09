from flask import Flask, render_template, request, redirect,url_for,abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SECRET_KEY'] ='dangal'
db = SQLAlchemy(app)

#user table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    firstname = db.Column(db.String(20),nullable=False)
    lastname = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(100), nullable=False)
    passwords = db.relationship('Passwords', backref='owner')

#passwords table
class Passwords(db.Model):
    #feilds with datatype
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(50),nullable=False)
    website = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(50),nullable=False)
    #foreign key
    owner_username = db.Column(db.Integer, db.ForeignKey('users.username'))

current_user=None
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    global current_user
    #declares message
    msg = ""
    #gets login details from form
    if request.method =='POST':
        username = request.form['user']
        password = request.form['pass']
        # checks if user is correct 
        connection = db.session.connection()
        query = f"SELECT username,password FROM users WHERE username=\"{username}\" AND password=\"{password}\";"
        user_correct = connection.execute(query).first() is not None
        print(user_correct)
        if user_correct:
            #sets current user as the user from form
            msg=""
            current_user = connection.execute(query).first()
            return redirect(url_for('view_psw'))
            print('user correct')
        else:
            #sets message
            msg = 'Wrong user or pass'
    return render_template('login.html',msg=msg)

@app.route('/signup',methods=['GET','POST'])
def signup():
    global current_user
    #declares message
    msg = ""
    #gets detail from form
    if request.method == "POST":
        username = request.form['user']
        password = request.form['pass']
        firstname = request.form['fn']
        lastname = request.form['ln']
        msg =""
        #checks if user exists
        user_free = Users.query.filter_by(username=username).first() is None
        if user_free:
            #if user doesnot exists then adds the user
            user = Users(username=username, firstname=firstname, lastname=lastname, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            msg = 'User already exists'
    return render_template('signup.html',msg=msg)

@app.route('/add_psw',methods= ['GET','POST'])
def add_psw():
    #checks if logged in or not
    global current_user
    if current_user is not None:
        if request.method == 'POST':
            #gets detail from form
            email = request.form['email']
            website = request.form['website']
            password = request.form['pass']
            #puts detail in instance of password table
            passwords = Passwords(email=email,website=website,password=password,owner_username=current_user.username)
            #adds details in table
            db.session.add(passwords)
            db.session.commit()
        return render_template('add_psw.html')
    else:
        #if not logged in shows 403 error
        return abort(403)
    

@app.route('/view_psw')
def view_psw():
    global current_user
    #checks if logged in
    if current_user is not None:
        #instance of passwords with details
        passwords = Passwords.query.filter_by(owner_username=current_user.username)
        
        return render_template('view_psw.html',user=current_user,passwords=passwords)
    else:
        #if not logged in shows 403 error
        return abort(403)

@app.route('/logout')
def logout():
    current_user = None
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True,port=8080)