from flask import Flask, render_template, request, url_for, flash, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost:3306/project_manager"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '\x11s\x16\x07q\xe4_g\x02\x94Y7\x0e\xc2\xa6\xe7\xd55t\x1az\xd7\x1a'
db = SQLAlchemy(app)

class Project(db.Model):
    __tablename__='projects'
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length = 100))

    task = db.relationship("Task", cascade = "all, delete-orphan")

class Task(db.Model):
    __tablename__='tasks'
    task_id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(length=250))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    project = db.relationship("Project", backref = 'project')
    task_name = db.Column(db.String(length=100))
    priority = db.Column(db.String(length=10))

db.create_all()

@app.route("/")
def show_projects():
    return render_template("index.html", projects = Project.query.all())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/project/<project_id>")
def show_task(project_id):
    return render_template("project_task.html", project = Project.query.filter_by(project_id = project_id).first(), tasks = Task.query.filter_by(project_id=project_id).all())

@app.route("/add/project", methods = ["POST"])
def add_project():
    if not request.form['project-title']:
        flash("Enter the title for your new project", "red")
    else:
        project = Project(title=request.form['project-title'])
        db.session.add(project)
        db.session.commit()
        flash("Project added successfully", "green")
    return redirect(url_for('show_projects'))

@app.route("/project/add/task/<project_id>", methods = ["POST"])
def add_task(project_id):
    task = Task(task_name=request.form['task_name'], description=request.form['task-description'], project_id=project_id, priority=request.form['priority'])
    db.session.add(task)
    db.session.commit()
    flash("Task added successfully", "green")
    return redirect(url_for('show_task', project_id = project_id))

@app.route("/delete/task/<task_id>", methods=["POST"])
def delete_task(task_id):
    pending_delete_task = Task.query.filter_by(task_id=task_id).first()
    original_project_id = pending_delete_task.project.project_id
    db.session.delete(pending_delete_task)
    db.session.commit()
    return redirect(url_for('show_task', project_id = original_project_id))

@app.route("/delete/project/<project_id>", methods=["POST"])
def delete_project(project_id):
    pending_delete_project = Project.query.filter_by(project_id=project_id).first()
    db.session.delete(pending_delete_project)
    db.session.commit()
    return redirect(url_for('show_projects'))

@app.route("/update/task/<task_id>", methods=['POST'])
def to_update(task_id):
    return render_template('update.html', task_id=task_id)

@app.route("/update/edit_task/<task_id>", methods=['POST'])
def edit_task(task_id):
    if not request.form['task-description']:
        flash("Enter the task details for your task", "red")
    else:
        edit_task = Task.query.filter_by(task_id=task_id).first()
        edit_task.description = request.form['task-description']
        project_id = edit_task.project_id
        db.session.commit()
    return redirect(url_for('show_task', project_id = project_id ))


app.run(debug=True, host='127.0.0.1',port=3000)
