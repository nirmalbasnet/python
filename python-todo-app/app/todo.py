from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from . import db
from datetime import datetime


bp = Blueprint('todos', __name__, url_prefix='/todos')


@bp.route('/', methods=('GET', 'POST'))
def todo_list():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        error = None
        if not title or not description:
            error = 'Please fill the title and description'

        if error is None:
            try:
                db_obj = db.open_connection()
                cursor = db_obj.cursor()
                query = 'INSERT INTO todos (title, description, user_id, created_at) VALUES (%s, %s, %s, %s)'
                cursor.execute(query, (title, description,
                               g.user['user_id'], datetime.now()))
                cursor.close()
                db_obj.commit()

                return redirect(url_for('todos.todo_list'))
            except Exception as e:
                db_obj.rollback()
                error = str(e)
            finally:
                db.close_connection()

        if error is not None:
            flash(error)

    try:
        db_obj = db.open_connection()
        cursor = db_obj.cursor()
        query = 'SELECT id, title, description, created_at, completed_at FROM todos WHERE user_id = %s'
        cursor.execute(query, (g.user['user_id'],))
        todos = cursor.fetchall()
        cursor.close()

        response = []

        for (id, title, description, created, completed) in todos:
            response.append({
                'id': id,
                'title': title,
                'description': description,
                'created': created,
                'completed': completed,
            })
    except Exception as e:
        print(e)
    finally:
        db.close_connection()

    return render_template('todos/index.html', todos=response)


@bp.route('/delete/<id>', methods=('GET', 'POST'))
def delete_todo(id):
    try:
        db_obj = db.open_connection()
        cursor = db_obj.cursor()
        query = 'DELETE FROM todos WHERE id = %s'
        cursor.execute(query, (id,))
        cursor.close()
        db_obj.commit()
    except Exception as e:
        print(e)
        db_obj.rollback()
    finally:
        db.close_connection()

    return redirect(url_for('todos.todo_list'))


@bp.route('/update/<id>', methods=('GET', 'POST'))
def update_todo(id):
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']

            db_obj = db.open_connection()
            cursor = db_obj.cursor()
            query = 'UPDATE todos SET title=%s, description=%s WHERE id = %s'
            cursor.execute(query, (title, description, id))
            cursor.close()
            db_obj.commit()

            return redirect(url_for('todos.todo_list'))
        except Exception as e:
            print(e)
            db_obj.rollback()
        finally:
            db.close_connection()

    try:
        db_obj = db.open_connection()
        cursor = db_obj.cursor()
        query = 'Select id, title, description FROM todos WHERE id = %s'
        cursor.execute(query, (id,))
        todo = cursor.fetchone()
        cursor.close()

        (todo_id, title, description) = todo
        update_todo_data = {
            'id': todo_id,
            'title': title,
            'description': description
        }
    except Exception as e:
        print(e)
    finally:
        db.close_connection()

    return render_template('todos/index.html', update_todo=update_todo_data)


@bp.route('/complete/<id>')
def complete_todo(id):
    try:
        db_obj = db.open_connection()
        cursor = db_obj.cursor()
        query = 'UPDATE todos SET completed_at=%s WHERE id = %s'
        cursor.execute(query, (datetime.now(), id))
        cursor.close()
        db_obj.commit()

        return redirect(url_for('todos.todo_list'))
    except Exception as e:
        error = str(e)
        db_obj.rollback()
    finally:
        db.close_connection()


@bp.before_app_request
def check_auth():
    current_route = request.endpoint
    auth_token = request.cookies.get('auth_token')

    if auth_token is None and current_route in ['todos.todo_list']:
        return redirect(url_for('auth.login'))

    if auth_token is not None and current_route in ['todos.todo_list']:
        try:
            from . import jwt
            decoded_token = jwt.decode(auth_token)
            g.user = decoded_token
        except Exception as e:
            print(e)
            return redirect(url_for('auth.login'))

    return None
