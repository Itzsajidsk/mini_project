import logging
import pymysql

# Use PyMySQL as a drop-in replacement for MySQLdb (avoids compiling mysqlclient)
# IMPORTANT: install_as_MySQLdb() must run before any module imports that load MySQLdb
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Dev-only dummy credentials (used when registration is disabled)
DEV_DUMMY_USERNAME = ''
DEV_DUMMY_PASSWORD = ''
DEV_MODE_ALLOW_ANY_LOGIN = True  # Development mode: if True and a username is not found, allow login with any password
DEV_PERSIST_ANY_LOGIN = True  # if True, persist the dynamically-logged-in user into the DB

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flames_login'

mysql = MySQL(app)

# Debugging: Test MySQL Connection
with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        print("✅ MySQL connection successful!")
        cur.close()
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")

# Ensure users table exists
with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        mysql.connection.commit()
        cur.close()
        print("✅ Users table checked/created successfully.")
    except Exception as e:
        print(f"❌ Error creating users table: {e}")

    # Create a dummy user for local testing if it does not exist
    try:
        with mysql.connection.cursor() as cur:
            dummy_username = 'testuser'
            dummy_password_raw = 'password123'  # change to desired dummy password
            # Check if exists
            cur.execute("SELECT * FROM users WHERE username = %s", (dummy_username,))
            if cur.fetchone() is None:
                from passlib.hash import sha256_crypt
                hashed = sha256_crypt.hash(dummy_password_raw)
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (dummy_username, hashed))
                mysql.connection.commit()
                print(f"✅ Dummy user '{dummy_username}' created for testing.")
            else:
                print(f"ℹ️ Dummy user '{dummy_username}' already exists.")
    except Exception as e:
        print(f"❌ Error creating dummy user: {e}")

# Ensure user_names table exists (to store user's entered/display names)
with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_names (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                display_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        mysql.connection.commit()
        cur.close()
        print("✅ user_names table checked/created successfully.")
    except Exception as e:
        print(f"❌ Error creating user_names table: {e}")

# Ensure relationships table exists (to store pairs of names entered for FLAMES)
with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                name1 VARCHAR(100) NOT NULL,
                name2 VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        mysql.connection.commit()
        cur.close()
        print("✅ relationships table checked/created successfully.")
    except Exception as e:
        print(f"❌ Error creating relationships table: {e}")

# Routes
@app.route('/')
def home():
    if 'logged_in' in session:
          return render_template('index.html')
    else:
        return redirect(url_for('login'))







@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('❌ Username and password are required.', 'danger')
            return render_template('register.html')

        try:
            hashed = sha256_crypt.hash(password)
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
                mysql.connection.commit()
            flash('✅ Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"❌ Error during registration: {e}")
            flash('❌ Registration failed. Username might already exist.', 'danger')

    return render_template('register.html')







@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        # Debugging: Print received login data
        print(f"Login Attempt: Username={username}")

        try:
            with mysql.connection.cursor() as cur:
                result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
                if result > 0:
                    data = cur.fetchone()
                    stored_password = data[2]  # Password is in the 3rd column (0-based index)

                    # Verify password
                    if sha256_crypt.verify(password_candidate, stored_password):
                        session['logged_in'] = True
                        session['username'] = username
                        flash('✅ Login successful!', 'success')
                        return redirect(url_for('home'))
                    else:
                        flash('❌ Incorrect password!', 'danger')
                else:
                    # If username not found in DB, allow dev dummy login as a fallback
                    if DEV_MODE_ALLOW_ANY_LOGIN:
                        session['logged_in'] = True
                        session['username'] = username
                        flash('✅ Dev fallback login successful!', 'success')
                        logging.info(f"Dev fallback login used for username: {username}")
                        if DEV_PERSIST_ANY_LOGIN:
                            try:
                                with mysql.connection.cursor() as cur2:
                                    cur2.execute("SELECT * FROM users WHERE username = %s", (username,))
                                    if cur2.fetchone() is None:
                                        from passlib.hash import sha256_crypt as _sha
                                        cur2.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, _sha.hash(password_candidate)))
                                        mysql.connection.commit()
                                        print(f"✅ Persisted dynamic dev user '{username}' into DB.")
                            except Exception as e:
                                logging.error(f"Error persisting dynamic dev user: {e}")
                        return redirect(url_for('home'))
                    else:
                        flash('❌ Username not found!', 'danger')
        except Exception as e:
            logging.error(f"❌ Error during login: {e}")
            flash('❌ Login failed. Please try again.', 'danger')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('✅ You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/save_relationship', methods=['POST'])
def save_relationship():
    if 'logged_in' not in session:
        return {"status": "error", "message": "Not authenticated"}, 401

    username = session.get('username')
    data = request.get_json() if request.is_json else request.form
    name1 = data.get('name1')
    name2 = data.get('name2')

    if not name1 or not name2:
        return {"status": "error", "message": "Both names required"}, 400

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("INSERT INTO relationships (username, name1, name2) VALUES (%s, %s, %s)", (username, name1, name2))
            mysql.connection.commit()
        logging.info(f"Saved relationship for {username}: {name1} & {name2}")
        return {"status": "ok", "message": "Saved"}, 200
    except Exception as e:
        logging.error(f"Error saving relationship for {username}: {e}")
        return {"status": "error", "message": "DB error"}, 500



if __name__ == '__main__':
    app.run(debug=True)
