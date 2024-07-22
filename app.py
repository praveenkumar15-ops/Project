from flask import Flask, render_template, url_for, request, redirect
import mysql.connector

app = Flask(__name__)

# Establish the database connection
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Praveen@1527',
        database='madam'
    )
    cursor = connection.cursor()
except mysql.connector.Error as e:
    print('MySQL connector is not connecting', e)
    cursor = None
    connection = None

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/')
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/')
@app.route('/doctor')
def doctor():
    return render_template('doctors.html')

@app.route('/appointment',methods=['GET','POST'])
def appointment():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        mobile = request.form['mob']
        gen = request.form['sex']
        app = request.form['app']
        text = request.form['text']
        try:
            cursor.execute('INSERT INTO appointment(fname, lname, email, mobile, gen, app, text) VALUES(%s, %s, %s, %s, %s, %s, %s)', (fname, lname, email, mobile, gen, app, text))
            print(fname, lname, email, mobile, gen, app, text)
            connection.commit()
        except:
            print ('Failed to insert appointment')
        return redirect(url_for('display'))
    
@app.route('/display')
def display():
    cursor.execute('select * from appointment')
    value=cursor.fetchall()
    print(value)
    return render_template('appointment.html',data=value)

@app.route('/edit/<int:id>')
def edit(id):
    cursor.execute('select * from appointment  where app_id=%s',(id,))
    value=cursor.fetchone()
    return render_template('update.html',data=value)
            
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        id = request.form['id']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        mobile = request.form['mob']
        gen = request.form['sex']
        app = request.form['app']
        text = request.form['text']
        print(id)
        try:
            cursor.execute('Update appointment set fname=%s, lname=%s, email=%s, mobile=%s, gen=%s, app=%s, text=%s where app_id=%s', (fname, lname, email, mobile, gen, app, text,id))
            print(fname, lname, email, mobile, gen, app, text)
            connection.commit()
        except:
            print ('Failed to insert appointment')
        return redirect(url_for('display'))

@app.route('/delete/<id>')
def delete(id):
    if cursor and connection:
        try:
            cursor.execute('delete from appointment  where app_id=%s',(id,))
            print('Deleted appointment')
            connection.commit()
            return redirect('display')
        except mysql.connector.Error as e:
            print('Failed to delete data from MySQL table:', e)
    return redirect(url_for('display'))

if __name__ == '__main__':
    app.run(debug=True)