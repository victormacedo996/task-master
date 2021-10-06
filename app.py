from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='development'
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db = SQLAlchemy(app)

    class Todo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(200), nullable=False)
        date_created= db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return '<Task %r>' % self.id

    @app.route('/', methods=['POST', 'GET'])
    def index ():
        if request.method == "POST":
            task_content = request.form['content']
            new_task = Todo(content=task_content)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return 'there was a issue adding your task'
        else:
            tasks = Todo.query.order_by(Todo.date_created).all()
            return render_template("index.html", tasks=tasks)

    @app.route('/delete/<int:id>')
    def delete(id):
        task_to_delete = Todo.query.get_or_404(id)

        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem deleting that task'

    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    def update(id):
        task = Todo.query.get_or_404(id)
        if request.method == "POST":
            task.content = request.form['content']

            try:
                db.session.commit()
                return redirect('/')
            except:
                return 'There was a problem updating that task'
        else:
            return render_template('update.html', task=task)

    return app



if __name__ == "__main__":
    create_app()