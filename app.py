# importing libraries and flask
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from models import Schema
from service import ServiceUser
from functools import wraps
import sqlite3
from wtforms import Form, StringField, PasswordField, IntegerField, TextAreaField, validators
from passlib.hash import sha256_crypt
# from flask_mysqldb import MySQL
# from flask_script import Manager
from datetime import datetime


#creating instance for flask
app = Flask(__name__)

# index
@app.route('/')
def index():
    # return "hello"
    return redirect(url_for('login'))

# LoginHome
@app.route('/loginHome')
def loginHome():
    return render_template('loginHome.html')

# home page
@app.route('/home')
def home():
    return render_template('home.html')

# Form for creating new User in database
@app.route('/newUser')
def newUser():
    return render_template('newUserForm.html')


@app.route('/newUserSubmit', methods=['POST'])
def newUserSubmit():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user_type = request.form['user_type']
    if user_type == 'Developer':
        type = 2
    else:
        type = 1


    params = {}
    params['name'] = name
    params['email'] = email
    params['password'] = password
    params['type'] = type

    if name == '' or email == '' or password == '':
        flash("please fill all fields", 'warning')
        return redirect(url_for('newUser'))
    else:
        answer = ServiceUser().create(params)
        print(answer)
        flash("New User created !", 'success')
        return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == '' or password == '':
            flash("please fill all fields",  'warning')
            return render_template('login.html')
        params = {}
        params['email'] = email
        result = ServiceUser().reads(params)
        print(result)
        # return render_template('login.html')
        if result is not None:
            password_candidate = result[3]
            user_type = result[4]
            if password_candidate == password:
                # **********************************************************
                if session.get('logged_in') is None:
                    session['checked_in'] = False
                    session['checked_out'] = True
                # # ************************************************************
                session['logged_in'] = True
                session['username'] = email
                session['user_type'] = user_type
                session['password'] = password
                if user_type == 1:
                    flash('You are now logged in', 'success')
                    # return "you are hr! "
                    return redirect(url_for('employerHome'))
                else:
                    flash('You are now logged in', 'success')
                    # return "you are employee"
                    return redirect(url_for('employeeHome'))
            else:
                error = 'Invalid password'
                return render_template('login.html', error=error)
        else:
            error = 'username not found'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# Check if user logged in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('loginHome'))
    return wrap

# check if admin is logged in or not


def is_logged_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['user_type'] == 1:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Employee Logout *********
@app.route('/employeeLogout')
@is_logged_in
def employeeLogout():
    session['logged_in'] = False
    flash('You are now logged out employee', 'success')
    return redirect(url_for('login'))


# Employer Home
@app.route('/employerHome')
@is_logged_admin
def employerHome():
    return render_template('employerHome.html')

# Employee Home
@app.route('/employeeHome', methods=['GET', 'POST'])
@is_logged_in
def employeeHome():
    if request.method == 'GET':
        return render_template('employeeHome.html')
    else:
        tick1 = 0
        tick2 = 0
        eswar = dict(request.form)
        if eswar['action']==['id1']:
            tick1 = 1
        else:
            tick2 = 1
        app.logger.info('Post request recieved')
        email = session['username']
        entered_date = request.form['leave_date']
        year, month, dte = entered_date.split('-')
        app.logger.info(year)
        conn = sqlite3.connect('pms.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM leaves WHERE email = ? and date = ? ", (email, entered_date))
        sameresult = cur.fetchone()
        app.logger.info(sameresult)
        if sameresult is not None:
            flash('You have already taken leave on requested date','warning')
            app.logger.info(sameresult)
            cur.close()
            return redirect(url_for('employeeHome'))
        cur.execute("SELECT * FROM working_data WHERE email = ? and year = ? and month = ? ", (email,year,month))
        result = cur.fetchall()
        if result is not None:
            data = cur.fetchone()
            cur.execute("SELECT * FROM user_details WHERE email = ?", [email])
            data2 = cur.fetchall()
            if len(data2) == 0:
                flash('You are yet to be entered into system fully by HR executive ', 'warning')
                return redirect(url_for('employeeHome'))
            eswar = dict(request.form)
            app.logger.info(eswar['action'])
            if eswar['action'] == ['id1']:
                app.logger.info('in if')
                # app.logger.info(data2[])
                if data2[6] > data[4]:
                    cur.execute("SELECT * FROM leaves WHERE email = ? and date = ?", (email, entered_date))
                    result3 = cur.fetchall()
                    if result3 is not None:
                        flash('casual leave is already granted on that date', 'warning')
                        cur.close()
                        return redirect(url_for('employeeHome'))
                    else:
                        flash('casual leave granted', 'success')
                        val = 1 + data[4]
                        session['leave'] = True
                        cur.execute("insert into leaves(email, date, type) values(?, ?, ?)", (email, entered_date, 1))
                        cur.execute("update working_data set casual_leaves = ? where email = ? and year = ? and month = ? ",(val,email,year,month))
                        conn.commit()
                else:
                    flash('you have reached your maximum casual leaves', 'warning')
                    cur.close()
                    return redirect(url_for('employeeHome'))
            else:
                app.logger.info('in else')
                if data2[7] > data[3]:
                    cur.execute("SELECT * FROM leaves WHERE email = ? and date = ? ", (email, entered_date))
                    result3 = cur.fetchall()
                    if result3 is not None:
                        flash('sick leave is already granted on that date', 'warning')
                        cur.close()
                        return redirect(url_for('employeeHome'))
                    else:
                        flash('sick leave granted', 'success')
                        val = 1 + data['sick_leaves']
                        cur.execute("update working_data set sick_leaves =  ?  where email =  ?  and year =  ?  and month =  ? ", (val, email, year, month))
                        cur.execute("insert into leaves(email, date, type) values( ? ,  ? ,  ? )", (email, entered_date, 2))
                        conn.commit()
                else:
                    flash('you have reached your maximum sick leaves', 'warning')
                    cur.close()
                    return redirect(url_for('employeeHome'))
        else:
            if tick1 == 1:
                flash('Casual leave granted', 'success')
            else:
                flash('Sick leave granted', 'success')
            cur.execute("insert into working_data(email, year, month,sick_leaves,casual_leaves,working_hours) values( ? ,  ? ,  ? , ? , ? , ? )", (email,year,month,tick2,tick1,0))
        conn.commit()
        cur.close()
        return redirect(url_for('employeeHome'))
#
# #admin req needes***********
# #Check in********************
#
# Check if it is a leave for an user:<username> on the day he is checking in
def checkLeave(username, date):
    conn = sqlite3.connect('pms.db')
    cur = conn.cursor()
    cur.execute("select * from leaves where email= ? and date= ? ", (username, date))
    result = cur.fetchall()
    if len(result) == 0:
        cur.close()
        return False
    else:
        cur.close()
        return True
#
@app.route('/checkin')
@is_logged_in
def checkin():
    conn = sqlite3.connect('pms.db')
    date = datetime.now().date()
    if session['checked_in'] == True:
        flash('already checked in', 'warning')
        return redirect(url_for('employeeHome'))
    else:
        if checkLeave(session['username'], date):
            flash('Today is a leave for you', 'warning')
            return redirect(url_for('employeeHome'))
        else:
            flash('You are checked in', 'success')
            session['checked_in'] = True
            session['checked_out'] = False
            session['checkin'] = datetime.now()
            return redirect(url_for('employeeHome'))
# #*******
# #*********************************************
#
#
#
@app.route('/checkout')
@is_logged_in
def checkout():
    conn = sqlite3.connect('pms.db')
    if session['checked_out'] == True:
        flash('already checked out', 'warning')
        return redirect(url_for('employeeHome'))
    else:
        flash('you are checked out', 'success')
        session['checked_in'] = False
        session['checked_out'] = True
        session['checkout'] = datetime.now()
        workingdur = session['checkout'] - session['checkin']
        email = session['username']
        year = session['checkin'].year
        month = session['checkin'].month
#         #*******SQL QUERY
        cur = conn.cursor()
        cur.execute("SELECT * FROM working_data WHERE email =  ?  and year =  ?  and month =  ? ", (email, year, month))
        result = cur.fetchone()
        if result is not None:
            app.logger.info('check1')
            data = result
            totalworking = data[5]
        else:
            app.logger.info('check2')
            cur.execute("insert into working_data(email, year, month,sick_leaves,casual_leaves,working_hours) values( ? ,  ? ,  ? , ? , ? , ?  )", (email,year,month,0,0,0))
            conn.commit()
            totalworking = 0

        totalworking = totalworking +(workingdur.seconds/3600.0)
        cur.execute("update working_data set working_hours =  ?  where email =  ?  and year =  ?  and month =  ? ",(totalworking,email,year,month))
        conn.commit()
        cur.close()
#         #******
#         #calculate time and date based on
        return redirect(url_for('employeeHome'))


@app.route('/employeeInfo/<string:username>', methods=['GET', 'POST'])
@is_logged_in
def employeeInfo(username):
    conn = sqlite3.connect('pms.db')
    if request.method != 'POST':
        cur = conn.cursor()
        bun = datetime.now()
        year = bun.year
        month = bun.month
        app.logger.info(month)
        cur.execute("select * from user_details where email= ? ",[username])
        row = cur.fetchone()
        cur.execute("select * from working_data where email= ?  and year =  ?  and month =  ? ",(username,year,month))
        prow = cur.fetchone()
        app.logger.info(prow)
        return render_template('employeeInfo.html', row=row, prow=prow)
        if prow is not None:
            cur.close()

            '''
            rows = cur.fetchall()
            for row in rows:
                if row['email']==username:
                    app.logger.info(row)
                    return render_template('employeeInfo.html', row=row)
                    cur.close()
                    break
            '''
    else:
        eswar = dict(request.form)
        app.logger.info('Post request recieved')
        name = request.form['username']
        email = session['username']
        salaryPerHour = request.form['salaryPerHour']
        jobTitle = request.form['jobTitle']
        payInOvertime = request.form['payInOvertime']
        maxCasualLeaves = request.form['maxCasualLeaves']
        maxSickLeaves = request.form['maxSickLeaves']
        cur = conn.cursor()
        app.logger.info(eswar)
        if eswar['action'] == ['update']:
            cur.execute("update user_details set name = ? , salary_per_hr = ? , job_title= ? , pay_in_overtime= ? , max_casual_leaves= ? , max_sick_leaves= ?  where email= ? ", (name, salaryPerHour, jobTitle, payInOvertime, maxCasualLeaves, maxSickLeaves, username))
            flash("Details updated Succesfully", 'success')
        else:
            cur.execute('delete from user_details where email= ? ', [username])
            cur.execute('delete from User where email= ? ', [username])
            cur.execute('delete from leaves where email= ? ', [username])
            cur.execute('delete from working_data where email= ? ', [username])
            flash('employee deleted successfully', 'success')
        conn.commit()
        cur.close()
        return render_template('employerHome.html')




# View Employees
@app.route('/viewEmployees', methods=['GET', 'POST'])
@is_logged_admin
def viewEmployees():
    conn = sqlite3.connect('pms.db')
    if request.method == 'GET':
        cur = conn.cursor()
        cur.execute("select * from user_details where email in (select email from User where type=2)")
        result = cur.fetchall()
        if len(result) > 0:
            rows = result
            app.logger.info('Hello')
            return render_template('viewEmployees.html', rows=rows)
            cur.close()
        else:
            flash('No employees found', 'info')
            return render_template('employerHome.html')
    else:
        app.logger.info('IN POST')
        # date = request.form['salary_date']
        date = datetime.now()
        app.logger.info(date)
        month_year = request.form['salary_month_year']
        year, month = month_year.split('-')
        app.logger.info(year, ' ', month)
        app.logger.info(year)
        cur = conn.cursor()
        cur.execute("select * from (working_data join user_details  on working_data.email = user_details.email) where working_data.email in (select email from working_data where year =  ?  and month =  ? ) and working_data.month= ? ",(year,month,month))
        result = cur.fetchall()
        if len(result) > 0:
            rows = result
            # # app.logger.info(rows)
            # salary = []
            for row in rows:
                row.update( {"salary":0})
            for row in rows:
                row['salary'] = (row['working_hours']+row['sick_leaves']*6+row['casual_leaves']*6)*row['salary_per_hr']
                app.logger.info(row['salary'])
                # salary['value'] = row['working_hours']*
                # app.logger.info(dict[i]['email'] + ' and ' + dict[i]['salary'])
            return render_template('salary_generate.html', rows = rows, date = date)
            # cur.close()
        else:
            flash('No employees worked in that month','info')
            return render_template('viewEmployees.html')
#
#
class NewEmployeeForm(Form):
    email = StringField('email', [validators.Length(min=6, max=50)])
    name = StringField('name', [validators.Length(min=1, max=50)])
    salaryPerHour = IntegerField('salaryPerHour', [validators.NumberRange(min=1, max=100000)])
    jobTitle = StringField('jobTitle', [validators.Length(min=1, max=50)])
    payInOvertime = IntegerField('payInOvertime', [validators.NumberRange(min=1, max=100000)])
    maxCasualLeaves = IntegerField('maxCasualLeaves', [validators.NumberRange(min=0, max=10)])
    maxSickLeaves = IntegerField('maxSickLeaves', [validators.NumberRange(min=0, max=10)])

# Add Employee
@app.route('/newEmployee', methods=['GET', 'POST'])
@is_logged_admin
def newEmployee():
    conn = sqlite3.connect('pms.db')
    form = NewEmployeeForm(request.form)
    if request.method == 'POST' and form.validate():
        app.logger.info('got a request as POST')
        print("got the data from the form")
        name = form.name.data
        email = form.email.data
        salaryPerHour = form.salaryPerHour.data
        jobTitle = form.jobTitle.data
        payInOvertime = form.payInOvertime.data
        maxCasualLeaves = form.maxCasualLeaves.data
        maxSickLeaves = form.maxSickLeaves.data
        date = datetime.now().date()

        cur = conn.cursor()
        cur.execute("select * from User where email= ? ", [email])
        result = cur.fetchall()
        if len(result) > 0:
            flash('username already taken', 'warning')
            return render_template('newEmployee.html')
        cur.execute("insert into User (name, email, password, type) values(?, ? ,  ? ,  ? )", (name, email, '0000', 2))
        conn.commit()
#
        cur.execute("insert into user_details(email, name, salary_per_hr, joining_date, job_title, pay_in_overtime, max_casual_leaves, max_sick_leaves) values( ? ,  ? ,  ? ,  ? ,  ? ,  ? ,  ?, ? )", (email, name, salaryPerHour, date, jobTitle, payInOvertime, maxCasualLeaves, maxSickLeaves))
        query = """
                        insert into working_data (email,year,month,sick_leaves,casual_leaves,working_hours) values(?, ?, ?,?,? , ?)
                        """
        bun = datetime.now()
        cur.execute(query, (email, bun.year, bun.month, 0, 0, 0))
        conn.commit()

        cur.execute("")

        cur.close()

        flash('New User has been added to the database', 'success')

        return redirect(url_for('employerHome'))
    else:
        if request.method == 'POST':
            flash('Please fill all blanks','warning')
    return render_template('newEmployee.html', form=form)


# Employee Data
@app.route('/employeeData')
@is_logged_in
def employeeData():
    return render_template('employeeData')

# Update Password
@app.route('/updatePassword', methods=['GET', 'POST'])
@is_logged_in
def updatePassword():
    conn = sqlite3.connect('pms.db')
    if request.method=='POST':
        app.logger.info('postdone')
        cur = conn.cursor()
        currentPassword = request.form['currentPassword']
        newPassword = request.form['newPassword']
        if newPassword=='' or currentPassword =='':
            flash('Please fill all feilds','warning')
            return render_template('updatePassword.html')
        if currentPassword == session['password']:
            cur.execute("update User set password= ?  where email= ? ",(newPassword,session['username']))
            flash('Your password has been updated, Use this password from next login','success')
            conn.commit()
            cur.close()
            if session['user_type'] ==1:
                return redirect(url_for('logout'))
            return redirect(url_for('employeeLogout'))
        else:
            flash('Please fill correct password','warning')
            return render_template('updatePassword.html')
    else:
        app.logger.info('getdone')
        return render_template('updatePassword.html')


if __name__ == '__main__':
    app.secret_key = 'hel#33'
    # app.debug = True
    # manager = Manager(app)
    # manager.run()
    Schema()
    app.run(debug=True)

