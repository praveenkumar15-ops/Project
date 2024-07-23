from flask import Flask, request, redirect, url_for, render_template, session, flash
import re
import mysql.connector
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Praveen@1527',
        database='Task_Manager'
    )
    cursor = conn.cursor()
except mysql.connector.Error as e:
    print("Error connecting to MySQL database:", e)
    conn = mysql.connector

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            msg = 'Logged in successfully!'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email,))
                conn.commit()
                msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/index' , methods=['GET', 'POST'] )
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        user_id = session['user_id']
        if cursor:
            try:
                cursor.execute('SELECT * FROM tasks WHERE user_id = %s', (user_id,))
                tasks = cursor.fetchall()
                
                print("Fetched tasks:", tasks)  # Debug output
                return render_template("dashboard.html", tasks=tasks)
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                return render_template('dashboard.html', msg='An error occurred. Please try again later.')
        else:
            return render_template('dashboard.html', msg='Database connection error.')
    return redirect(url_for('login'))

# @app.route('/view_tasks')
# def view_task
#     if 'loggedin' not in session:
#         return redirect(url_for('login'))

#     user_id = session['user_id']
#     conn = get_db_connection()
#     if conn is None:
#         flash('Could not connect to the database')
#         return render_template('view_tasks.html', data=[])

#     cursor = conn.cursor(dictionary=True)

#     # Fetch total number of items
#     cursor.execute('SELECT COUNT(*) AS count FROM tasks WHERE user_id = %s', (user_id,))
    
#     # Get the current page number from the query parameter, default to 1

#     # Fetch tasks for the current page
#     query = '''
#         SELECT tasks.task_id, tasks.title, tasks.description, category.category_name as category, 
#                tasks.priority, tasks.due_date, tasks.created_at, tasks.updated_at
#         FROM tasks
#         LEFT JOIN category ON tasks.category_id = category.category_id
#         WHERE tasks.user_id = %s
        
#     '''
#     cursor.execute(query, (user_id))
#     data = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return render_template('view_tasks.html')


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'loggedin' in session:
        msg = ''
        categories = []
        if cursor:
            try:
                cursor.execute('SELECT * FROM category')
                categories = cursor.fetchall()
            except mysql.connector.Error as e:
                print("Error fetching categories:", e)
        
        if request.method == 'POST':
            print("Form data:", request.form)  # Debug output
            if 'title' in request.form and 'description' in request.form and 'category_id' in request.form and 'priority' in request.form:
                title = request.form['title']
                description = request.form['description']
                user_id = session['user_id']
                category_id = request.form['category_id']
                priority = request.form['priority']
                due_date = request.form['due_date']

                # Check if category exists
                cursor.execute("SELECT * FROM category WHERE category_id = %s", (category_id,))
                category_exists = cursor.fetchone()
                print("Category exists:", category_exists)  # Debug output

                if not category_exists:
                    msg = 'Category does not exist!'
                    return render_template("add_task.html", msg=msg, categories=categories)

                cursor.execute("INSERT INTO tasks (user_id, title, description, category_id, priority, due_date) VALUES (%s, %s, %s, %s, %s, %s)", 
                               (user_id, title, description, category_id, priority, due_date))
                conn.commit()
                msg = 'You have successfully added the task!'
                return redirect(url_for('dashboard'))
            else:
                msg = 'Please fill out the form completely!'
        return render_template("add_task.html", msg=msg, categories=categories)
    return redirect(url_for('login'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'loggedin' in session:
        cursor.execute('DELETE FROM tasks WHERE task_id = %s AND user_id = %s', (task_id, session['user_id']))
        conn.commit()
        return redirect(url_for('dashboard'))

@app.route("/update/<task_id>", methods=['POST', 'GET'])
def update(task_id):
    cursor.execute("SELECT * FROM tasks where task_id = %s", (task_id,))
    task = cursor.fetchone()
    return render_template('edit_task.html', task=task)

@app.route('/edit_task/<int:task_id>', methods=['GET','POST'])
def edit_task(task_id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM tasks WHERE task_id = %s AND user_id = %s', (task_id, session['user_id']))
        task = cursor.fetchone()
        if task:
            return render_template('edit_task.html', task=task)
        else:
            return 'Task not found or access denied', 404
    return redirect(url_for('login'))

@app.route('/edit_tasks/<int:task_id>', methods=['GET', 'POST'])
def edit_tasks(task_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            print("Request method is POST")  # Debug output
            print("Request form data:", request.form)  # Debug output

            title = request.form.get('title')
            description = request.form.get('description')

            print("Title:", title)  # Debug output
            print("Description:", description)  # Debug output

            if title and description:
                cursor.execute('UPDATE tasks SET title = %s, description = %s WHERE task_id = %s AND user_id = %s',
                               (title, description, task_id, session['user_id']))
                conn.commit()
                return redirect(url_for('dashboard'))
            else:
                return 'Please fill out the form completely!', 400
    return redirect(url_for('login'))

@app.route('/view_task/<int:task_id>', methods=['GET', 'POST'])
def view_task(task_id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM tasks WHERE task_id = %s', (task_id,))
        task = cursor.fetchone()
        if task:
            return render_template('view_task.html', task=task)
        else:
            return 'Task not found or access denied', 404
    return redirect(url_for('login'))
# @app.route('/view_by_cat/<int:category_id>', methods=['GET', 'POST'])
# def view_by_cat(category_id):
#     if 'loggedin' in session:
#         try:
#             cursor.execute('SELECT * FROM tasks where category_id=%s and user_id=%s',(category_id,session['user_id']))
#             categories = cursor.fetchall()
#             return render_template('view_by_cat.html', categories=categories)
#         except mysql.connector.Error as e:
#             print("Error fetching categories:", e)
#             return render_template('view_by_cat.html', msg='An error occurred. Please try again later.')
#     return redirect(url_for('login'))
@app.route('/view_by_cat', methods=['GET', 'POST'])
def view_by_cat():
    if 'loggedin' in session:
        msg = ''
        categories = []
        tasks = []
        try:
            cursor.execute('SELECT * FROM category')
            categories = cursor.fetchall()
            
            if request.method == 'POST':
                category_id = request.form['category_id']
                cursor.execute('SELECT * FROM tasks WHERE category_id = %s AND user_id = %s', (category_id, session['user_id']))
                tasks = cursor.fetchall()
        except mysql.connector.Error as e:
            print("Error fetching categories or tasks:", e)
            msg = 'An error occurred. Please try again later.'
        return render_template('view_by_cat.html', categories=categories, tasks=tasks, msg=msg)
    return redirect(url_for('login'))
# @app.route('/view_by_pri', methods=['GET', 'POST'])
# def view_by_pri():
#     priority = request.form.get('priority', 'Low')
#     tasks = []  # This should be replaced with a real query to the database
#     return render_template('view_by_pri.html', priority=priority, tasks=tasks)

@app.route('/view_by_pri', methods=['GET', 'POST'])
def view_by_pri():
    if 'loggedin' in session:
        priority = request.form.get('priority', 'Low')
        tasks = []
        try:
            cursor.execute('SELECT * FROM tasks WHERE priority = %s AND user_id = %s', (priority, session['user_id']))
            tasks = cursor.fetchall()
        except mysql.connector.Error as e:
            print("Error fetching tasks by priority:", e)
            return render_template('view_by_pri.html', priority=priority, tasks=tasks, msg='An error occurred. Please try again later.')
        return render_template('view_by_pri.html', priority=priority, tasks=tasks)
    return redirect(url_for('login'))




@app.route('/view_due_dates')
def view_due_dates():
    tasks = [
        # Example data; replace with actual database query results
        
    ]
    return render_template('view_due_dates.html', tasks=tasks)

@app.route('/category{/<int:task_id>')
def category(task_id):
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM category WHERE category_id = %s', (task_id,))
        task = cursor.fetchone()
        if task:
            return render_template('category_insert.html', task=task)
        else:
            return 'Task not found or access denied', 404
    return redirect(url_for('login'))

@app.route('/category_insert', methods=['GET', 'POST'])
def category_insert():
    if 'loggedin' in session:
        if request.method == 'POST':
            category_name = request.form['category_name']
            
           
            try:
                cursor.execute('INSERT INTO category (catagory_name) VALUES (%s)', (category_name,))
                print(category_name)
                conn.commit()
                return redirect(url_for('dashboard'))
            except mysql.connector.Error as e:
                print("Error inserting into categories table:", e)
                return 'An error occurred. Please try again later.'
        return render_template('category_insert.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
