from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
app.jinja_env.globals.update(year=datetime.now().year)

# Database initialization
def get_db():
    db = sqlite3.connect('website.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes for public pages
@app.route('/')
def index():
    try:
        db = get_db()
        apps = db.execute('SELECT * FROM apps WHERE is_enabled = 1 ORDER BY click_count DESC').fetchall()
        about = db.execute('SELECT content FROM pages WHERE type = "about"').fetchone()
        contact = db.execute('SELECT content FROM pages WHERE type = "contact"').fetchone()
        return render_template('index.html', apps=apps, about=about, contact=contact)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('index.html', apps=[], about=None, contact=None)

@app.route('/click/<int:app_id>')
def track_click(app_id):
    try:
        db = get_db()
        app = db.execute('SELECT link, is_enabled FROM apps WHERE id = ?', [app_id]).fetchone()
        
        if not app:
            flash('App not found.', 'error')
            return redirect(url_for('index'))
            
        if not app['is_enabled']:
            flash('This app is currently disabled.', 'error')
            return redirect(url_for('index'))
            
        db.execute('UPDATE apps SET click_count = click_count + 1 WHERE id = ?', [app_id])
        db.commit()
        return redirect(app['link'])
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'logged_in' in session:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            user = db.execute('SELECT * FROM admin WHERE username = ?', [username]).fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                session['logged_in'] = True
                flash('Welcome back, admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            flash('Invalid username or password.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        db = get_db()
        apps = db.execute('SELECT * FROM apps ORDER BY click_count DESC').fetchall()
        return render_template('admin/dashboard.html', apps=apps)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/admin/apps/add', methods=['GET', 'POST'])
@login_required
def add_app():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            thumbnail = request.form['thumbnail'].strip()
            link = request.form['link'].strip()
            
            if not all([name, thumbnail, link]):
                flash('All fields are required.', 'error')
                return render_template('admin/add_app.html')
                
            db = get_db()
            db.execute(
                'INSERT INTO apps (name, thumbnail_path, link, is_enabled) VALUES (?, ?, ?, 1)',
                [name, thumbnail, link]
            )
            db.commit()
            flash('App added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    return render_template('admin/add_app.html')

@app.route('/admin/apps/edit/<int:app_id>', methods=['GET', 'POST'])
@login_required
def edit_app(app_id):
    try:
        db = get_db()
        if request.method == 'POST':
            name = request.form['name'].strip()
            thumbnail = request.form['thumbnail'].strip()
            link = request.form['link'].strip()
            
            if not all([name, thumbnail, link]):
                flash('All fields are required.', 'error')
                app = db.execute('SELECT * FROM apps WHERE id = ?', [app_id]).fetchone()
                return render_template('admin/edit_app.html', app=app)
                
            db.execute(
                'UPDATE apps SET name = ?, thumbnail_path = ?, link = ? WHERE id = ?',
                [name, thumbnail, link, app_id]
            )
            db.commit()
            flash('App updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        app = db.execute('SELECT * FROM apps WHERE id = ?', [app_id]).fetchone()
        if not app:
            flash('App not found.', 'error')
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/edit_app.html', app=app)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/apps/toggle/<int:app_id>')
@login_required
def toggle_app(app_id):
    try:
        db = get_db()
        app = db.execute('SELECT is_enabled FROM apps WHERE id = ?', [app_id]).fetchone()
        if not app:
            flash('App not found.', 'error')
            return redirect(url_for('admin_dashboard'))
            
        new_status = not app['is_enabled']
        db.execute('UPDATE apps SET is_enabled = ? WHERE id = ?', [new_status, app_id])
        db.commit()
        flash(f'App {"enabled" if new_status else "disabled"} successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/apps/delete/<int:app_id>')
@login_required
def delete_app(app_id):
    try:
        db = get_db()
        app = db.execute('SELECT name FROM apps WHERE id = ?', [app_id]).fetchone()
        if not app:
            flash('App not found.', 'error')
            return redirect(url_for('admin_dashboard'))
            
        db.execute('DELETE FROM apps WHERE id = ?', [app_id])
        db.commit()
        flash(f'App "{app["name"]}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/pages', methods=['GET', 'POST'])
@login_required
def manage_pages():
    try:
        db = get_db()
        if request.method == 'POST':
            about_content = request.form['about_content'].strip()
            contact_content = request.form['contact_content'].strip()
            
            if not about_content or not contact_content:
                flash('Both About Us and Contact Us content are required.', 'error')
                about = db.execute('SELECT content FROM pages WHERE type = "about"').fetchone()
                contact = db.execute('SELECT content FROM pages WHERE type = "contact"').fetchone()
                return render_template('admin/manage_pages.html', about=about, contact=contact)
                
            db.execute('UPDATE pages SET content = ? WHERE type = "about"', [about_content])
            db.execute('UPDATE pages SET content = ? WHERE type = "contact"', [contact_content])
            db.commit()
            flash('Pages updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        about = db.execute('SELECT content FROM pages WHERE type = "about"').fetchone()
        contact = db.execute('SELECT content FROM pages WHERE type = "contact"').fetchone()
        return render_template('admin/manage_pages.html', about=about, contact=contact)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    if not os.path.exists('website.db'):
        init_db()
    app.run(debug=True)
