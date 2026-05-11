from flask import Flask, render_template, request, redirect, session, send_file
from medicine_inventory import get_status
from database import connect_db, create_table
import pandas as pd

app = Flask(__name__)

app.secret_key = "medicine_secret_key"

create_table()


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = connect_db()

        user = conn.execute(

            '''

            SELECT * FROM users

            WHERE username = ? AND password = ?

            ''',

            (username, password)

        ).fetchone()

        conn.close()

        if user:

            session['user'] = username

            return redirect('/')

        else:

            return render_template(
                'login.html',
                error="Invalid Username or Password"
            )

    return render_template('login.html')


# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = connect_db()

        try:

            conn.execute(

                '''

                INSERT INTO users (username, password)

                VALUES (?, ?)

                ''',

                (username, password)

            )

            conn.commit()

            conn.close()

            return redirect('/login')

        except:

            conn.close()

            return render_template(
                'register.html',
                error="Username already exists"
            )

    return render_template('register.html')


# LOGOUT
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# HOME PAGE
@app.route('/')
def home():

    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search', '')

    conn = connect_db()

    if search:

        medicines = conn.execute(

            '''

            SELECT * FROM medicines

            WHERE name LIKE ?

            ''',

            ('%' + search + '%',)

        ).fetchall()

    else:

        medicines = conn.execute(
            'SELECT * FROM medicines'
        ).fetchall()

    conn.close()

    inventory = []

    expired_count = 0
    low_stock_count = 0
    expiring_soon_count = 0

    for item in medicines:

        medicine = dict(item)

        medicine['status'] = get_status(medicine)

        if "EXPIRED" in medicine['status']:
            expired_count += 1

        elif "LOW STOCK" in medicine['status']:
            low_stock_count += 1

        elif "Expiring Soon" in medicine['status']:
            expiring_soon_count += 1

        inventory.append(medicine)

    total_medicines = len(inventory)

    return render_template(

        'index.html',

        inventory=inventory,

        total_medicines=total_medicines,

        expired_count=expired_count,

        low_stock_count=low_stock_count,

        expiring_soon_count=expiring_soon_count,

        search=search,

        username=session['user']

    )


# ALERTS PAGE
@app.route('/alerts')
def alerts():

    if 'user' not in session:
        return redirect('/login')

    conn = connect_db()

    medicines = conn.execute(
        'SELECT * FROM medicines'
    ).fetchall()

    conn.close()

    alerts_list = []

    for item in medicines:

        medicine = dict(item)

        medicine['status'] = get_status(medicine)

        if medicine['status'] != "🟢 OK":

            alerts_list.append(medicine)

    return render_template(
        'alerts.html',
        alerts=alerts_list
    )


# EXPORT CSV
@app.route('/export')
def export_csv():

    if 'user' not in session:
        return redirect('/login')

    conn = connect_db()

    medicines = conn.execute(
        'SELECT * FROM medicines'
    ).fetchall()

    conn.close()

    data = []

    for item in medicines:

        medicine = dict(item)

        medicine['status'] = get_status(medicine)

        data.append(medicine)

    df = pd.DataFrame(data)

    file_name = "medicine_inventory.csv"

    df.to_csv(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )


# ADD MEDICINE
@app.route('/add', methods=['GET', 'POST'])
def add_medicine():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        name = request.form['name']
        category = request.form['category']
        supplier = request.form['supplier']
        stock = request.form['stock']
        expiry = request.form['expiry']

        conn = connect_db()

        conn.execute(

            '''

            INSERT INTO medicines

            (name, category, supplier, stock, expiry)

            VALUES (?, ?, ?, ?, ?)

            ''',

            (name, category, supplier, stock, expiry)

        )

        conn.commit()

        conn.close()

        return redirect('/')

    return render_template('add_medicine.html')
# DELETE MEDICINE
@app.route('/delete/<int:id>')
def delete_medicine(id):

    if 'user' not in session:
        return redirect('/login')

    conn = connect_db()

    conn.execute(
        'DELETE FROM medicines WHERE id = ?',
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect('/')


# UPDATE MEDICINE
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_medicine(id):

    if 'user' not in session:
        return redirect('/login')

    conn = connect_db()

    medicine = conn.execute(
        'SELECT * FROM medicines WHERE id = ?',
        (id,)
    ).fetchone()

    if request.method == 'POST':

        name = request.form['name']
        category = request.form['category']
        supplier = request.form['supplier']
        stock = request.form['stock']
        expiry = request.form['expiry']

        conn.execute(

            '''

            UPDATE medicines

            SET

            name = ?,
            category = ?,
            supplier = ?,
            stock = ?,
            expiry = ?

            WHERE id = ?

            ''',

            (

                name,
                category,
                supplier,
                stock,
                expiry,
                id

            )

        )

        conn.commit()

        conn.close()

        return redirect('/')

    conn.close()

    return render_template(
        'update_medicine.html',
        medicine=medicine
    )


if __name__ == '__main__':
    app.run(debug=True)