from . import db
from flask import Blueprint, redirect, request, render_template, url_for, flash, make_response
from datetime import datetime, timedelta


from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        db_obj = db.open_connection()
        error = None

        if not name or not email or not password:
            error = 'Please enter all the required fields'

        if error is None:
            try:
                cursor = db_obj.cursor()
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(
                    query,
                    (name, email, generate_password_hash(password)),
                )
                cursor.close()
                db_obj.commit()
            except Exception as e:
                error = str(e)
            else:
                return redirect(url_for("auth.login"))
            finally:
                db.close_connection()

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        error = None

        if not email or not password:
            error = 'Please input your credential'

        if error is None:
            try:
                db_obj = db.open_connection()
                cursor = db_obj.cursor()

                query = 'SELECT id, name, email, password FROM users WHERE email = %s'
                cursor.execute(query, (email,))
                user = cursor.fetchone()

                if not user:
                    error = 'Invalid credential!'

                (user_id, user_name, user_email, user_password) = user

                validate_password = check_password_hash(
                    user_password, password
                )

                if not validate_password:
                    error = 'Invalid credential!'

                if error is None:
                    from . import jwt
                    payload = {
                        "user_id": user_id,
                        "user_name": user_name,
                        "email": user_email,
                        "exp": datetime.now() + timedelta(hours=1)
                    }
                    token = jwt.encode(payload)
            except Exception as e:
                print(e)
                error = 'Unalbe to login with gven credential!'
            else:
                response = make_response(redirect(url_for('todos.todo_list')))
                response.set_cookie('auth_token', token)
                return response
            finally:
                db.close_connection()

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def check_auth():
    current_route = request.endpoint
    auth_token = request.cookies.get('auth_token')

    if auth_token is not None and current_route in ['auth.register', 'auth.login']:
        try:
            from . import jwt
            if jwt.decode(auth_token):
                return redirect(url_for('todos.todo_list'))
        except Exception as e:
            print(e)
    return None
