from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask import session, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



app.secret_key = "supersecretkey"

# --- MySQL Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@localhost/portfolio_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Model ---
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)



# ✅ Create the table automatically
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    projects = Project.query.all()  # Fetch all uploaded projects
    return render_template('index.html', projects=projects)

def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        new_msg = Message(name=name, email=email, phone=phone, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash('Message sent successfully!', 'success')

    # Fetch all projects from DB
    projects = Project.query.all()

    return render_template('index.html', projects=projects)


# --- Admin Credentials ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# --- Admin Login Page ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('admin_login.html',datetime=datetime)


# --- Admin Dashboard ---
@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'warning')
        return redirect(url_for('admin_login'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    projects=Project.query.order_by(Project.id.desc()).all()
    return render_template('admin_dashboard.html', messages=messages,projects=projects, datetime=datetime)

@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    if "admin_logged_in" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]

        # Handle image upload
        image_file = request.files["image"]
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)
            image = f"uploads/{filename}"
        else:
            image = "uploads/default.jpg"  # fallback image

        # Save to database
        new_project = Project(title=title, description=description, category=category, image=image)
        db.session.add(new_project)
        db.session.commit()

        flash("Project added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_project.html")


# --- Edit Project ---
@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.image = request.form.get('image')
        project.description = request.form.get('description')
        project.category = request.form.get('category')
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_project.html', project=project)


# --- Delete Project ---
@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'danger')
    return redirect(url_for('admin_dashboard'))



# --- Delete Message ---
@app.route('/delete/<int:id>')
def delete_message(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
