from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import bcrypt
import datetime
import random
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'login_database'
}

# SQL queries to create tables
sql_queries = [
    # Create credentials table
    
    
    "CREATE TABLE IF NOT EXISTS PANCHAYATH (VILLAGE_CODE VARCHAR(10) UNIQUE PRIMARY KEY, PINCODE INT, VILLAGE_ADDRESS VARCHAR(30), VILLAGE_NAME VARCHAR(20) )",
    
    "CREATE TABLE IF NOT EXISTS USER (AADHAR_NO VARCHAR(13) UNIQUE PRIMARY KEY, NAME VARCHAR(50), CARD_NUMBER VARCHAR(10), OCCUPATION VARCHAR(20), INCOME INT, CONTACT VARCHAR(11), EMAIL VARCHAR(30), VILLAGE_CODE VARCHAR(10), ADDRESS VARCHAR(30), FOREIGN KEY (VILLAGE_CODE) REFERENCES PANCHAYATH(VILLAGE_CODE) on DELETE CASCADE on update CASCADE )",
    
    "CREATE TABLE IF NOT EXISTS EMPLOYEE (EMPLOYEE_ID VARCHAR(10) UNIQUE PRIMARY KEY, EMPLOYEE_NAME VARCHAR(20), CONTACT VARCHAR(11), EMAIL VARCHAR(30),ADDRESS TEXT, VILLAGE_CODE VARCHAR(10), FOREIGN KEY(VILLAGE_CODE) REFERENCES PANCHAYATH(VILLAGE_CODE) on DELETE CASCADE on update CASCADE )",
    
    "CREATE TABLE IF NOT EXISTS SCHEME (SCHEME_ID VARCHAR(10) UNIQUE PRIMARY KEY, SCHEME_NAME text, DOMAIN text, DESCRIPTION text, EMPLOYEE_ID VARCHAR(10), FOREIGN KEY(EMPLOYEE_ID) REFERENCES EMPLOYEE(EMPLOYEE_ID) on DELETE CASCADE on update CASCADE )",
    
    "CREATE TABLE IF NOT EXISTS OPTIONS (SCHEME_ID VARCHAR(10), VILLAGE_CODE VARCHAR(10), PRIMARY KEY(SCHEME_ID, VILLAGE_CODE), FOREIGN KEY(SCHEME_ID) REFERENCES SCHEME(SCHEME_ID) on DELETE CASCADE on update CASCADE, FOREIGN KEY(VILLAGE_CODE) REFERENCES PANCHAYATH(VILLAGE_CODE) on DELETE CASCADE on update CASCADE )",
    
    "CREATE TABLE IF NOT EXISTS REGISTER (SCHEME_ID VARCHAR(10), AADHAR_NO VARCHAR(13), APPLICATION_NO int UNIQUE, VILLAGE_ID VARCHAR(10), STATUS VARCHAR(20), DATE DATE, PRIMARY KEY(APPLICATION_NO), FOREIGN KEY(VILLAGE_ID) REFERENCES PANCHAYATH(VILLAGE_CODE) on DELETE CASCADE on update CASCADE, FOREIGN KEY(SCHEME_ID) REFERENCES OPTIONS(SCHEME_ID) on DELETE CASCADE on update CASCADE, FOREIGN KEY(AADHAR_NO) REFERENCES USER(AADHAR_NO) on DELETE CASCADE on update CASCADE )",
    
    "CREATE TABLE IF NOT EXISTS CREDENTIALS (USERNAME VARCHAR(50) PRIMARY KEY, PASSWORD VARCHAR(255) NOT NULL, AADHAR_NO VARCHAR(13), EMPLOYEE_ID VARCHAR(10), LOGIN_TYPE VARCHAR(12), FOREIGN KEY (AADHAR_NO) REFERENCES USER(AADHAR_NO) on DELETE CASCADE on update CASCADE, FOREIGN KEY (EMPLOYEE_ID) REFERENCES EMPLOYEE(EMPLOYEE_ID) on DELETE CASCADE on update CASCADE, CONSTRAINT CK_CREDENTIALS_TYPE CHECK ( (AADHAR_NO IS NOT NULL AND EMPLOYEE_ID IS NULL) OR (EMPLOYEE_ID IS NOT NULL AND AADHAR_NO IS NULL) ) )"

    # Add more SQL queries for other tables
]


triggers= """
    CREATE TRIGGER IF NOT EXISTS set_status_before_insert
BEFORE INSERT ON REGISTER
FOR EACH ROW
begin
    SET NEW.STATUS = 'Submitted';
end;
    """

# Function to initialize tables
def init_tables():
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Execute SQL queries to create tables
    for query in sql_queries:
        cursor.execute(query)
    #cursor.execute(triggers)
    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    
username=None


def insert_panchayath_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert or update data from Village.csv into PANCHAYATH table
        with open('Village.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                village_code, pincode, village_address, village_name = row
                sql = "REPLACE INTO PANCHAYATH (VILLAGE_CODE, PINCODE, VILLAGE_ADDRESS, VILLAGE_NAME) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (village_code, pincode, village_address, village_name))

        # Insert or update data from Employee.csv into EMPLOYEE table
        with open('Employee.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                id, name, contact, mail, address, vc = row
                sql = "REPLACE INTO EMPLOYEE (EMPLOYEE_ID, EMPLOYEE_NAME, CONTACT, EMAIL, ADDRESS, VILLAGE_CODE) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (id, name, contact, mail, address, vc))

        # Insert or update data from Employee_credentials.csv into CREDENTIALS table
        with open('Employee_credentials.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                Username, Password, Employee_Id, type = row
                sql = "REPLACE INTO CREDENTIALS (USERNAME, PASSWORD, EMPLOYEE_ID, LOGIN_TYPE) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (Username, Password, Employee_Id, type))

        # Insert or update data from Schemes.csv into SCHEME table
        with open('Schemes.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                scheme_id, scheme_name, domain, description, employee_id = row
                sql = "REPLACE INTO SCHEME (SCHEME_ID, SCHEME_NAME, DOMAIN, DESCRIPTION, EMPLOYEE_ID) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (scheme_id, scheme_name, domain, description, employee_id))

        # Insert or update data from Options.csv into OPTIONS table
        with open('Options.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                scheme_id, village_code = row
                sql = "REPLACE INTO OPTIONS (SCHEME_ID, VILLAGE_CODE) VALUES (%s, %s)"
                cursor.execute(sql, (scheme_id, village_code))

        conn.commit()
        print("Data inserted successfully.")

    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        cursor.close()
        conn.close()

def get_options(username):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute SQL query to retrieve data
        cursor.execute("SELECT s.SCHEME_ID, s.SCHEME_NAME, s.DOMAIN, s.DESCRIPTION FROM SCHEME s, CREDENTIALS C WHERE C.EMPLOYEE_ID = s.EMPLOYEE_ID AND C.USERNAME=%s",(username,))

        # Fetch all rows
        options_data = cursor.fetchall()
        print(options_data)
        # Close cursor and connection
        cursor.close()
        conn.close()

        return options_data     
        
        
def retrieve_options(username):
        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute SQL query to retrieve data
        cursor.execute("SELECT s.SCHEME_ID, s.SCHEME_NAME, s.DOMAIN, s.DESCRIPTION FROM OPTIONS o JOIN SCHEME s ON o.SCHEME_ID = s.SCHEME_ID JOIN USER u ON o.VILLAGE_CODE = u.VILLAGE_CODE JOIN CREDENTIALS c ON u.AADHAR_NO = c.AADHAR_NO WHERE c.USERNAME =%s",(username,))

        # Fetch all rows
        options_data = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        conn.close()

        return options_data
    
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Function to authenticate user
def authenticate_user(username, password, usertype, conn):
    cursor = conn.cursor()
    # Prepare SQL statement with parameterized query to prevent SQL injection
    sql = "SELECT * FROM credentials WHERE username=%s AND password=%s AND login_type=%s"
    cursor.execute(sql, (username, password, usertype))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return True  # User authenticated successfully
    else:
        return False  # Authentication failed

def get_village_id(adhaar):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT VILLAGE_CODE FROM USER WHERE AADHAR_NO = %s", (adhaar,))
    village = cursor.fetchone()[0]  # Assuming AADHAR_NO is the first column
    cursor.close()
    conn.close()
    return village

def get_village():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PANCHAYATH ")
    village = cursor.fetchall()  # Assuming AADHAR_NO is the first column
    cursor.close()
    conn.close()
    return village

def get_aadhaar(username):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT AADHAR_NO FROM CREDENTIALS WHERE USERNAME = %s", (username,))
    aadhaar_info = cursor.fetchone()[0]  # Assuming AADHAR_NO is the first column
    cursor.close()
    conn.close()
    return aadhaar_info

# Function to generate a random application number
def generate_application_number():
    return random.randint(100000, 999999)  # Adjust range as needed


def msg(message):
    return render_template('USER/message.html', message=message)

def show_user_profile():
   username = request.args.get('username')
   return {username}

def get_user_details(username, conn):
    cursor = conn.cursor(dictionary=True)
    # Prepare SQL statement to retrieve user details
    sql = "SELECT u.* FROM user u, credentials c WHERE u.aadhar_no=c.aadhar_no AND c.username= %s"
    cursor.execute(sql, (username,))
    user_details = cursor.fetchone()
    cursor.close()
    return user_details

# Function to fetch applications from the database based on username
def fetch_applications(username):
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="login_database"
    )

    cursor = conn.cursor(dictionary=True)

    # Query to fetch applications for the given username
    query = "SELECT APPLICATION_NO, SCHEME_ID, STATUS, DATE FROM REGISTER WHERE AADHAR_NO = (SELECT AADHAR_NO FROM CREDENTIALS WHERE USERNAME = %s)"
    cursor.execute(query, (username,))
    applications = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return applications


@app.route('/')
def index():
    #insert_panchayath_data()
    return render_template('BEGIN/START.html')

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['login_type']
        
        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        
        # Authenticate user
        if authenticate_user(username, password, usertype, conn):
            if usertype == 'user':
                return redirect(url_for('user_main', username=username))
            elif usertype == 'employee':
                return redirect(url_for('employee_main', username=username))
            elif usertype=='admin':
                return redirect(url_for('admin_main', username=username))
            
        else:
            error_message = 'Invalid credentials. Please try again.'
            return render_template('BEGIN/START.html', error_message=error_message)
    else:
        return render_template('/')



@app.route('/applying', methods=['POST'])
def apply_user():
    username = request.args.get('username')
    schemes = retrieve_options(username)
    print(username)
    if request.method == 'POST':
        # Retrieve form data
        aadhaar = request.form.get('adhaar')
        scheme_id = request.form.get('scheme_id')
        application_number = request.form.get('application_number')
        status = request.form.get('status')
        date_of_applying = request.form.get('date')
        village = request.form.get('village_ID')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        try:
            sql = "INSERT INTO REGISTER (SCHEME_ID, AADHAR_NO, VILLAGE_ID, APPLICATION_NO, STATUS, DATE) VALUES (%s, %s,%s, %s, %s, %s)"
            cursor.execute(sql, (scheme_id, aadhaar,village, application_number, status, date_of_applying))
            conn.commit()
            print("Form data inserted successfully into the REGISTER table.")
            return redirect(url_for('user_main', username=username))
        except mysql.connector.Error as err:
            print("Error:", err)
            return redirect(url_for('user_main',username=username))
        finally:
            cursor.close()
            conn.close()
    

@app.route('/USER/MAIN')
def user_main():
    username = request.args.get('username')
    print(username)
    schemes = retrieve_options(username)
    return render_template('USER/MAIN.html', username=username, schemes=schemes)

@app.route('/USER/REGISTER')
def user_reg():
    username = request.args.get('username')
    return render_template('USER/REGISTER.html', username=username)

@app.route('/reg', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        aadhaar = request.form['aadhaar']
        address = request.form['address']
        village_code = request.form['village-code']
        ration_card = request.form['ration_card']
        phone = request.form['phone']
        email = request.form['email']
        occupation = request.form['occupation']
        username = request.form['username']
        password = request.form['password']
        income = request.form['income']
        print(income)
        # Check if required fields are not empty
        if (name and aadhaar and username and password) is None:
            error_message = 'Name, Aadhaar Number, Username, and Password are required.'
            flash(error_message,'error')
            return redirect(url_for('msg', message=error_message))

        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert user registration data into the database
        try:
            sql = "INSERT INTO USER (NAME, AADHAR_NO, ADDRESS, VILLAGE_CODE, CARD_NUMBER, CONTACT, EMAIL, OCCUPATION, INCOME) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)"
            cursor.execute(sql, (name, aadhaar, address, village_code, ration_card, phone, email, occupation, income))
            credentials_sql = "INSERT INTO CREDENTIALS (USERNAME, PASSWORD, AADHAR_NO, LOGIN_TYPE) VALUES (%s, %s, %s, %s)"
            cursor.execute(credentials_sql, (username, password, aadhaar, 'user'))
            conn.commit()
        except mysql.connector.Error as err:
            # Handle any database errors
            message = f"Error: {err}"
            msg(message)
            return redirect(url_for('get_village'))


        # Close connection
        cursor.close()
        conn.close()

        # Redirect to login page after successful registration
        return render_template('BEGIN/START.html')

    else:
        # If the request method is GET, render the registration form
        return render_template('registration.html')

@app.route('/USER/CHECK')
def user_app_check():
    username = request.args.get('username')
    print(username)
    appl = fetch_applications(username)
    return render_template('USER/CHECK.html',username=username,applications=appl)

@app.route('/USER/APPLY')
def user_apply():
    username = request.args.get('username')
    adhaar=get_aadhaar(username)
    vc=get_village_id(adhaar)
    schemes = retrieve_options(username)
    ap_no=generate_application_number()
    date = datetime.date.today().strftime('%Y-%m-%d')
    return render_template('USER/APPLY.html', username=username,date=date, ap_no=ap_no,adhaar=adhaar,vc=vc,schemes=schemes)

@app.route('/USER/EDIT')
def user_edit():
        username = request.args.get('username')
        print(username)
        conn = mysql.connector.connect(**db_config)
        user_details = get_user_details(username, conn)
        conn.close()
        return render_template('USER/EDIT.html', username=username, user=user_details)
    
@app.route('/change', methods=['POST'])
def info_change():
    username = request.args.get('username')
    print(username)
    if request.method == 'POST':
        # Retrieve form data
        new_name = request.form.get('name')
        print(new_name)
        new_address = request.form.get('address')
        new_phone = request.form.get('contact')
        new_email = request.form.get('email')
        new_occupation = request.form.get('village_id')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            sql = "UPDATE USER SET NAME=%s, ADDRESS=%s, CONTACT=%s, EMAIL=%s, VILLAGE_CODE=%s WHERE AADHAR_NO IN (SELECT AADHAR_NO FROM CREDENTIALS WHERE USERNAME = %s)"
            cursor.execute(sql, (new_name, new_address, new_phone, new_email, new_occupation, username))
            conn.commit()

            flash('User information updated successfully!', 'success')
            return redirect(url_for('user_main', username=username))
        except mysql.connector.Error as err:

            flash(f"Error: {err}", 'error')
            return redirect(url_for('user_edit', username=username))
        finally:
            cursor.close()
            conn.close()

@app.route('/EMPLOYEE/MAIN')
def employee_main():
    username = request.args.get('username')
    op=get_options(username)
    return render_template('EMPLOYEE/MAIN.html', username=username,op=op)
    

@app.route('/EMPLOYEE/EDIT')
def employee_edit():
    username = request.args.get('username')
    
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        # Execute SQL query to fetch employee details
        sql = "SELECT * FROM EMPLOYEE WHERE EMPLOYEE_ID IN (SELECT EMPLOYEE_ID FROM CREDENTIALS WHERE USERNAME= %s)"
        cursor.execute(sql, (username,))
        employee = cursor.fetchone()
        print(employee)
        return  render_template('EMPLOYEE/EDIT.html', username=username,employee=employee)
    except mysql.connector.Error as err:
        # Handle any database errors
        flash(f"Error: {err}", 'error')
        return redirect(url_for('employee_main', username=username))
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()


@app.route('/edit_employee', methods=['POST'])
def emp_edit():
    username = request.args.get('username')
    print(username)
    if request.method == 'POST':
        # Retrieve form data
        emp_name = request.form.get('name')
        emp_contact = request.form.get('contact')
        emp_email = request.form.get('email')
        address = request.form.get('address')
        village_code = request.form.get('village_id')

        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        try:
            # Execute SQL UPDATE statement to update employee details
            sql = "UPDATE EMPLOYEE SET EMPLOYEE_NAME = %s, CONTACT = %s, EMAIL = %s, VILLAGE_CODE = %s,ADDRESS = %s WHERE EMPLOYEE_ID IN (SELECT EMPLOYEE_ID FROM CREDENTIALS WHERE USERNAME= %s)"
            cursor.execute(sql, (emp_name, emp_contact, emp_email, village_code, address, username))
            conn.commit()

            # Redirect to the employee edit page with success message
            flash('Employee details updated successfully!', 'success')
            return redirect(url_for('employee_main', username=username))  # Pass the username parameter
        except mysql.connector.Error as err:
            # Handle any database errors
            flash(f"Error: {err}", 'error')
            return redirect(url_for('employee_edit', username=username))  # Pass the username parameter
        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
            
@app.route("/EMPLOYEE/VIEWFORMS")
def viewforms():
     username = request.args.get('username')
     conn = mysql.connector.connect(**db_config)
     cursor = conn.cursor(dictionary=True) 
     query = """
        SELECT R.APPLICATION_NO, R.SCHEME_ID, R.AADHAR_NO, R.VILLAGE_ID, R.STATUS, R.DATE
        FROM REGISTER R, OPTIONS O, EMPLOYEE E, SCHEME S
        WHERE R.SCHEME_ID = O.SCHEME_ID
        AND O.VILLAGE_CODE = E.VILLAGE_CODE
        AND R.VILLAGE_ID = E.VILLAGE_CODE
        AND R.STATUS != 'Approved'
        AND O.SCHEME_ID = S.SCHEME_ID
        AND E.EMPLOYEE_ID = S.EMPLOYEE_ID
        AND E.EMPLOYEE_ID IN (SELECT EMPLOYEE_ID FROM CREDENTIALS WHERE USERNAME=%s)
    """
     cursor.execute(query, (username,))
     register = cursor.fetchall()
     cursor.close()
     conn.close()
     print(register)
     return render_template('EMPLOYEE/VIEWFORMS.html',username=username,register=register)

@app.route('/chg', methods=['POST'])
@app.route('/change_form', methods=['POST'])
def change_form():
    username = request.args.get('username')
    if request.method == 'POST':
        # Retrieve form data
        application_numbers = request.form.getlist('application_number[]')
        statuses = request.form.getlist('status[]')

        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Loop through each form submission and update the database
        for application_number, status in zip(application_numbers, statuses):
            # Execute SQL UPDATE statement to update status
            sql = "UPDATE REGISTER SET STATUS = %s WHERE APPLICATION_NO = %s"
            cursor.execute(sql, (status, application_number))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Redirect to the employee edit page with success message
        flash('Employee details updated successfully!', 'success')
        return redirect(url_for('employee_main', username=username))
    
@app.route('/BEGIN/admin')
def admin_main():
    username = request.args.get('username')
    print(username)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # Execute SQL query to fetch employee details
    sql = "SELECT * FROM PANCHAYATH;"
    cursor.execute(sql, ())
    t1 = cursor.fetchall()
    print(t1)
    cursor.close()
    conn.close()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM USER;"
    cursor.execute(sql, ())
    t2 = cursor.fetchall()
    cursor.close()
    conn.close()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM EMPLOYEE;"
    cursor.execute(sql, ())
    t3 = cursor.fetchall()
    cursor.close()
    conn.close()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM CREDENTIALS;"
    cursor.execute(sql, ())
    t4 = cursor.fetchall()
    cursor.close()
    conn.close()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM SCHEME;"
    cursor.execute(sql, ())
    t5 = cursor.fetchall()
    cursor.close()
    conn.close()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM REGISTER;"
    cursor.execute(sql, ())
    t6 = cursor.fetchall()
    cursor.close()
    conn.close()
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM OPTIONS;"
    cursor.execute(sql, ())
    t7 = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('BEGIN/admin.html', username=username, t1=t1,t2=t2,t3=t3,t4=t4,t5=t5,t6=t6,t7=t7)

@app.route('/delete_row', methods=['GET', 'POST'])
def delete_row():
    
    if request.method == 'POST':
        table = request.form['table']
        pk=request.form['pk']
        id = request.form['id']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = f"DELETE FROM {table} WHERE {pk} = %s"
        cursor.execute(sql, (id,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('admin_main'))

@app.route('/delete_application', methods=['POST'])
def dlt_appl():
    conn = mysql.connector.connect(**db_config)
    username = request.form.get('username')
    apno = request.form.get('applicationNo')
    print(apno)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM REGISTER WHERE APPLICATION_NO = %s", (apno,))
    conn.commit()
    conn.close()
    return redirect(url_for('user_app_check', username=username))

@app.route("/EMPLOYEE/ACCEPTED")
def viewAcceptedForms():
     username = request.args.get('username')
     conn = mysql.connector.connect(**db_config)
     cursor = conn.cursor(dictionary=True)  # Set dictionary cursor
     query = """
        SELECT R.APPLICATION_NO, R.SCHEME_ID, R.AADHAR_NO, R.VILLAGE_ID, R.STATUS, R.DATE
        FROM REGISTER R, OPTIONS O, EMPLOYEE E
        WHERE R.SCHEME_ID = O.SCHEME_ID
        AND O.VILLAGE_CODE = E.VILLAGE_CODE
        AND R.VILLAGE_ID = E.VILLAGE_CODE
        AND R.STATUS='Approved' 
        AND E.EMPLOYEE_ID IN (SELECT EMPLOYEE_ID FROM CREDENTIALS WHERE USERNAME=%s)
    """
     cursor.execute(query, (username,))
     register = cursor.fetchall()
     print(register)
     cursor.close()
     conn.close()
     print(register)
     return render_template('EMPLOYEE/ACCEPTED.html',username=username,register=register)


@app.route('/edit_row', methods=['GET', 'POST'])
def edit_row():
    username = request.args.get('username')
    table = request.args.get('table')
    pk = request.args.get('pk')
    id = request.args.get('id')
    if request.method == 'GET':
        print(id)
        # Fetch data for the selected row to be edited
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        sql = f"SELECT * FROM {table} WHERE {pk} = {id}"
        cursor.execute(sql, ())
        row_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('BEGIN/edit.html', username=username, table=table, pk=pk, id=id, row_data=row_data)
    elif request.method == 'POST':
        print(id)
        print(pk)
        # Extract form data for the edited row
        edited_data = {key: request.form[key] for key in request.form if key not in ['table', 'pk', 'id']}
        #print(edited_data)
        # Perform update operation in the database
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        update_values = ', '.join([f'{key} = %s' for key in edited_data.keys()])
        print(update_values)
        #print(pk)
        #print(id)
        sql = f"UPDATE {table} SET {update_values} WHERE {pk} = {id}"
        print(sql)
        print(tuple(edited_data.values()))
        cursor.execute(sql, tuple(edited_data.values()))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Row updated successfully', 'success')
        # Redirect back to admin_main or appropriate page
        return redirect(url_for('admin_main', username=username))
    
@app.route('/getuser')
def getUserData():
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        ad=request.args.get('app_no')
        # Execute SQL query to retrieve data
        cursor.execute("SELECT * FROM USER WHERE AADHAR_NO=%s",(ad,))

        # Fetch all rows
        data = cursor.fetchall()
        print(data)
        # Close cursor and connection
        cursor.close()
        conn.close()

        return render_template('EMPLOYEE/INFO.html', data=data[0])

@app.route('/getuserdet')
def get_village():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PANCHAYATH;")
    village = cursor.fetchall()  # Assuming AADHAR_NO is the first column
    print(village)
    cursor.close()
    conn.close()
    return render_template('USER/REGISTER.HTML',vlg=village)

if __name__ == '__main__':
    # Initialize tables before starting the Flask app
    init_tables()
    app.run(debug=True)

