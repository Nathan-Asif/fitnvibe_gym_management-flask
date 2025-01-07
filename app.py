from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fitnvibe_flask'

mysql = MySQL(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(hashed_password, password):
    return hashed_password == hash_password(password)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("post received")
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT id, username, email, password FROM app_users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        
        print(user)
        hashed_password_from_db = user[3] 

        if user and verify_password(hashed_password_from_db, password):
            user_obj = User(id=user[0], username=user[1], email=user[2], role=user[3])
            login_user(user_obj)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('auth/login.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Site Title
app.config['SITE_TITLE'] = "FitnVibe"


# Database Objects
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

    @staticmethod
    def get(user_id):
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, username, email, role FROM app_users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        cur.close()
        if user:
            return User(id=user[0], username=user[1], email=user[2], role=user[3])
        return None
    
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Admin
@app.route('/admin/')
@login_required
def admin_dashboard():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM app_users WHERE role <> "admin"')
        total_users = cur.fetchone()[0]
        cur.execute('SELECT * FROM app_users')
        all_users = cur.fetchall()
        cur.execute('SELECT COUNT(*) FROM app_membershipplan')
        total_plans = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM app_membershipplan WHERE is_active = 1')
        active_memberships = cur.fetchone()[0]
        cur.close()
        
        user_details = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role
        }
        
        return render_template(
            'admin/dashboard.html',
            total_users=total_users,
            total_plans=total_plans,
            active_memberships=active_memberships,
            user=user_details,
            all_users=all_users
        )
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/admin/membership-plans')
@login_required
def admin_membership_plans():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM app_membershipplan')
        plans = cur.fetchall()
        cur.close()

        user_details = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role
        }

        return render_template(
            'admin/membership_plans.html', 
            plans=plans,
            user=user_details
        )
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/admin/membership-plans/create', methods=['GET', 'POST'])
@login_required
def create_membership_plan():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        features = request.form['features']
        icon_class = request.form['icon_class']
        is_active = 1 if 'is_active' in request.form else 0
        icon_color = request.form['icon_color']

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO app_membershipplan (name, price, features, icon_class, is_active, icon_color) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (name, price, features, icon_class, is_active, icon_color))
            mysql.connection.commit()
            cur.close()

            flash('Membership plan created successfully!', 'success')
            return redirect(url_for('admin_membership_plans'))

        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return redirect(url_for('create_membership_plan'))

    return render_template('admin/create_membership_plan.html')

@app.route('/admin/membership-plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def edit_membership_plan(plan_id):
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        features = request.form['features']
        icon_class = request.form['icon_class']
        is_active = 1 if 'is_active' in request.form else 0
        icon_color = request.form['icon_color']

        try:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE app_membershipplan SET name=%s, price=%s, features=%s, icon_class=%s, is_active=%s, icon_color=%s WHERE id=%s", 
                        (name, price, features, icon_class, is_active, icon_color, plan_id))
            mysql.connection.commit()
            cur.close()

            flash('Membership plan updated successfully!', 'success')
            return redirect(url_for('admin_membership_plans'))

        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return redirect(url_for('edit_membership_plan', plan_id=plan_id))

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM app_membershipplan WHERE id=%s", (plan_id,))
        plan = cur.fetchone()
        cur.close()

        if not plan:
            flash("Membership plan not found.", 'error')
            return redirect(url_for('admin_membership_plans'))

        return render_template('admin/edit_membership_plan.html', plan=plan)

    except Exception as e:
        flash(f"An error occurred: {e}", 'error')
        return redirect(url_for('admin_membership_plans'))

@app.route('/admin/membership-plans/delete/<int:plan_id>')
@login_required
def delete_membership_plan(plan_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM app_membershipplan WHERE id=%s", (plan_id,))
        mysql.connection.commit()
        cur.close()

        flash('Membership plan deleted successfully!', 'success')
        return redirect(url_for('admin_membership_plans'))

    except Exception as e:
        flash(f"An error occurred: {e}", 'error')
        return redirect(url_for('admin_membership_plans'))

@app.route('/admin/users/<int:user_id>')
@login_required
def view_user(user_id):
    """
    Fetches user details for display in a modal.

    Args:
        user_id (int): The ID of the user to view.

    Returns:
        A JSON response containing the user data.
    """
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM app_users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM app_users')
        result = cur.fetchall()
        cur.close()
        
        return f"Total records: {result[0]}"
    except Exception as e:
        return f"An error occurred: {e}"


@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM app_membershipplan')
    plans = cur.fetchall()
    cur.close()
    
    return render_template('home.html', plans=plans)

@app.route('/membership')
def membership():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM app_membershipplan')
    plans = cur.fetchall()
    cur.close()
    
    return render_template('membership.html', plans=plans)

@app.route('/about-us')
def about_us():
    return render_template('about_us.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact_us.html')

if __name__ == '__main__':
    # print(app.url_map)
    app.run(debug=True)