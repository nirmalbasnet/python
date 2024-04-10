import os
from flask import Flask, redirect, url_for


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    if config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(config)

    try:
        os.makedirs(app.instance_path, mode=0o777, exist_ok=True)
    except Exception as e:
        print(e)

    @app.route('/')
    def hello():
        return redirect(url_for('auth.login'))

    with app.app_context():
        from . import db
        db.init_db()

    from . import auth
    app.register_blueprint(auth.bp)

    from . import todo
    app.register_blueprint(todo.bp)

    return app
