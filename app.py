from flask import Flask
from flask import render_template, url_for, flash, request, redirect, Response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from controllers import products
from controllers.users import User

import sqlite3
import os

from forms import LoginForm

app = Flask(__name__)
SECRET_KEY = os.urandom(32)


app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('app.db')
    curs = conn.cursor()
    curs.execute("SELECT * from users where id = (?)", [user_id])
    lu = curs.fetchone()
    if lu is None:
        return None
    else:
        return User(int(lu[0]), lu[1], lu[2], lu[3])

@app.route('/home')
@app.route('/')
def index():
    prods = products.get_last_products()
    if current_user.is_authenticated:
        return render_template('home.html', prods=prods, user=current_user.get_data())
    return render_template('home.html', prods=prods)


@app.route('/category/<category_name>')
def category(category_name):
    category = category_name.replace('-', ' ')
    sub_cats = products.get_sub_categories(category)
    param = request.args.get('sub')
    if param != None:
        prods = products.get_products_by_sub_category(param)
    else:
        prods = products.get_products_by_category(category)

    if current_user.is_authenticated:
        return render_template('category.html', category=category, sub_category=param, sub_cats=sub_cats, prods=prods, user=current_user.get_data())
    return render_template('category.html', category=category, sub_category=param, sub_cats=sub_cats, prods=prods)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        conn = sqlite3.connect('app.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users where email = (?)",
                     [form.email.data])
        user = list(curs.fetchone())
        Us = load_user(user[0])
        if form.email.data == Us.email and form.password.data == Us.password:
            login_user(Us)
            names = Us.names
            # flash('Bienvenid@ '+names)
            return redirect(url_for('index'))
        else:
            flash('Las credenciales no son correctas.')

    return render_template('auth/login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/registro')
def registro():
    return render_template('auth/registro.html')
