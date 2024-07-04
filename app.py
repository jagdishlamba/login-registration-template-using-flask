from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from datetime import date
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class sqla:
    def __init__(self, db):
        self.db_url = (
            f'mysql+mysqlconnector://root:r0b0tic5@127.0.0.1:3306/{db}'
        )
        self.engine = create_engine(self.db_url)

    def gett(self, query):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Error: {e}")
            return None

    def exe(self, query):
        try:
            with self.engine.connect() as conn:
                conn.execute(text(query))
                conn.commit()
                conn.close()
                return True
        except SQLAlchemyError as e:
            print(f"Error: {e}")
            return False

    def __del__(self):
        if self.engine:
            self.engine.dispose()

# Configure MySQL connection
mycursor = sqla(db ="access_control")

app = Flask(__name__)
app.secret_key = "somerandomaiapplication"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
@app.route('/homepage')
def index():
   return render_template('home.html')


@app.route("/logout")
def logout():
    session["username"] = None
    return redirect("/login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        fac = request.form['fac']
        fullname = request.form['fullname']
        question =request.form['question']
        answer = request.form['answer']
        
        # Returns the current local date
        today = date.today()

        # Insert new user into the database
        query = f"INSERT INTO access_control.login_table (fullname, username, password, fac, question, answer, user_type, created_at) VALUES ('{fullname}','{username}','{password}','{fac}', '{question}', '{answer}', '{user_type}', '{today}');"
        z = mycursor.exe(query)
        if z:
            flash("Registration successsfull","success")
            return redirect(url_for('login'))
        else:
            flash("Error in registration","danger")
            return redirect(url_for('register'))     
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        query = f"SELECT * from `access_control`.`login_table` where (username='{username}' and password='{password}');"
        results = mycursor.gett(query)
        if len(results)!=0:
            session["username"] = username
            session["user_type"] = results[0][7]
            if results[0][7] == "superadmin":
                flash("Login successsfull","success")
                return redirect(url_for('superadminDashboard'))
            elif results[0][7] == "admin":
                flash("Login successsfull","success")
                return redirect(url_for('adminDashboard'))
            else:
                flash("Login successsfull","success")
                return redirect(url_for('clientDashboard'))
        else:
            flash("The Username or Password is not correct", "danger")
            return redirect(url_for('login'))
    else:
        if session.get("username") is not None:
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get("username") == None:
        return redirect(url_for('login'))
    else:
        if session["user_type"] =="superadmin":
            return redirect(url_for('superadminDashboard'))
        elif session["user_type"] == "admin":
            return redirect(url_for('adminDashboard'))
        else:
            return redirect(url_for('clientDashboard'))
    
@app.route('/superadminDashboard', methods=['GET', 'POST'])
def superadminDashboard():
    if session.get("username") == None:
        return redirect(url_for('login'))
    else:
        return render_template('superadminDashboard.html')

@app.route('/adminDashboard', methods=['GET', 'POST'])
def adminDashboard():
    if session.get("username") == None:
        return redirect(url_for('login'))
    else:
        return render_template('adminDashboard.html')

@app.route('/clientDashboard', methods=['GET', 'POST'])
def clientDashboard():
    if session.get("username") == None:
        return redirect(url_for('login'))
    else:
        return render_template('clientDashboard.html')


@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        username = request.form.get('username')
        question= request.form.get('question')
        answer = request.form.get('answer')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        if password != confirmPassword:
            flash("New Password did not match with confirm password", "danger")
            return redirect(url_for('forget'))
        else:
            query = f"SELECT * from `access_control`.`login_table` where (username='{username}' and question ='{question}');"
            results = mycursor.gett(query)
            
            if len(results)!=0:
                db_answer =  results[0][6]
                if answer == db_answer:
                    query = f"update `access_control`.`login_table` set password = '{password}' where username= '{username}';"
                    results = mycursor.exe(query)
                    if results:
                        flash("Password updated", "success")
                        return redirect(url_for('login'))
                    else:
                        flash("Error in updating password", "danger")
                        return redirect(url_for('forget'))
                else:
                    flash("Wrong Answer", "danger")
                    return redirect(url_for('forget'))
            else:
                flash("The Username or Question is not correct", "danger")
                return redirect(url_for('forget'))
    else:
        return render_template('forget_password.html')

# Ensure responses aren't cached 
@app.after_request
def add_header(r):
  r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
  r.headers["Pragma"] = "no-cache"    
  r.headers["Expires"] = "0"
  r.headers['Cache-Control'] = 'public, max-age=0'    
  return r

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
