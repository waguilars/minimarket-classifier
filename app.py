import datetime
import logging
from flask import Flask
from flask import render_template, url_for, flash, request, redirect, Response, make_response
from flask.json import jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from controllers import products
from controllers.users import User
from utils.clusters import get_clusters
from datetime import date, datetime, time

import sqlite3
import json
import os
import sys
import nltk

from forms import FormCarrito, LoginForm, ProductForm, RegisterForm


nltk.download('stopwords')

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
SECRET_KEY = os.urandom(32)
products.load_data()

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
    prods = prods[::-1]
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
    return render_template('category.html', category=category_name, sub_category=param, sub_cats=sub_cats, prods=prods)


@app.route('/carrito')
@login_required
def show_carrito():
    try:
        datos = json.loads(request.cookies.get(str(current_user.get_id())))
    except:
        datos = []
    articulos = []
    cantidades = []
    total = 0
    for articulo in datos:
        prod = products.get_product_by_id(articulo["id"])
        prod['PRICE'] = str(prod['PRICE']).replace(",", ".")
        prod['PRICE'] = float(prod['PRICE'])
        articulos.append(prod)
        cantidades.append(articulo["cantidad"])
        total = total + prod['PRICE'] * int(articulo["cantidad"])
    articulos = zip(articulos, cantidades)
    return render_template("cart.html", articulos=articulos, total=total, user=current_user.get_data())


@app.route('/carrito/add/<int:product_id>', methods=['POST', 'GET'])
@login_required
def add_cart(product_id):
    form = FormCarrito()
    form.id.data = product_id
    art = products.get_product_by_id(product_id)
    stock = int(art['STOCK'])

    if form.validate_on_submit():
        if stock >= int(form.cantidad.data):
            try:
                datos = json.loads(request.cookies.get(str(current_user.get_id())))
            except:
                datos = []
            actualizar = False
            for dato in datos:
                if dato["id"] == form.id.data:
                    dato["cantidad"] = form.cantidad.data + dato["cantidad"]
                    actualizar = True

            if not actualizar:
                datos.append({"id": form.id.data,
                              "cantidad": form.cantidad.data})
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie(str(current_user.get_id()), json.dumps(datos))
            return resp
        else:
            form.cantidad.errors.append("No hay artículos suficientes.")
    return render_template("cart_add.html", form=form, art=art, user=current_user.get_data())

@app.route('/carrito/delete/<int:id>')
def delete_item(id):
    try:
        datos = json.loads(request.cookies.get(str(current_user.get_id())))
    except:
        datos = []

    for item in datos:
        if item['id'] == id:
            datos.remove(item)

    resp = make_response(redirect(url_for('show_carrito')))
    resp.set_cookie(str(current_user.get_id()), json.dumps(datos))
    return resp

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

@app.route('/registro', methods=['POST', 'GET'])
def registro():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        conn = sqlite3.connect('app.db')
        curs = conn.cursor()
        new_user = (form.names.data, form.email.data, form.password1.data)
        curs.execute("insert into users(names, email, password) values(?,?,?);", new_user)
        conn.commit()
        flash('Usuario registrado correctamente')
        return redirect(url_for('login'))


    return render_template('auth/registro.html', form=form)

@app.route('/nuevo-producto', methods=['POST', 'GET'])
@login_required
def new_producto():
    form = ProductForm(request.form)
    categories = products.get_categories()
    user = current_user.get_data()

    if user['names'] != 'paty':
        return redirect(url_for('index'))
    if form.category.data is None:
        sub_categories = products.get_sub_categories(categories[0])
    else:
        sub_categories = products.get_sub_categories(form.category.data)

    form.category.choices = [(cat, cat) for cat in categories]
    form.sub_category.choices = [(sub, sub) for sub in sub_categories]

    if form.validate_on_submit():
        products.add_new(form.category.data, form.sub_category.data, form.product_name.data, form.price.data, form.stock.data, form.url_imagen.data)
        return redirect(url_for('index'))
    return render_template('add-producto.html', form=form, user=current_user.get_data())

@app.route('/data/sub-category/<category_name>')
def get_sub_categories(category_name):
    sub_categories = products.get_sub_categories(category_name)
    return jsonify(sub_categories)


@app.route('/checkout', methods=['POST'])
def make_payment():
    try:
        datos = json.loads(request.cookies.get(str(current_user.get_id())))
    except:
        datos = []
    if len(datos) == 0:
        return redirect(url_for('index'))

    date = datetime.now()
    date = datetime.timestamp(date)
    total = 0
    for item in datos:
        prod = products.get_product_by_id(item['id'])
        subtotal = prod['PRICE'] * item['cantidad']
        total += subtotal

    payment = (date, total, int(current_user.get_id()))

    conn = sqlite3.connect('app.db')
    curs = conn.cursor()
    curs.execute('insert into payments(date, total, user_id) values(?,?,?);', payment)
    payment_id = curs.lastrowid

    detail = []
    for item in datos:
        subtotal = prod['PRICE'] * item['cantidad']
        detail.append( (item['id'], item['cantidad'], subtotal, payment_id) )

    curs.executemany('insert into payment_detail(product_id, quantity, sub_total, payment_id) values(?,?,?,?);', detail)
    conn.commit()
    datos = []
    resp = make_response(render_template('thanks.html', user=current_user.get_data()))
    resp.set_cookie(str(current_user.get_id()), json.dumps(datos))
    return resp

@app.route('/compras')
@login_required
def get_compras():
    conn = sqlite3.connect('app.db')
    curs = conn.cursor()
    user_id = current_user.get_id()
    curs.execute("SELECT * FROM payments where user_id = (?)", [user_id])
    compras = list(curs.fetchall())
    detalle = []
    for compra in compras:
        obj = {
            "id": compra[0],
            "fecha": compra[1],
            "total": compra[2]
        }

        curs.execute("SELECT * FROM payment_detail where payment_id = (?)", [obj['id']])
        compra_detalle = list(curs.fetchall())
        detalle_prods = []
        if len(compra_detalle) > 0:
            for item in compra_detalle:
                prod_id = item[1]
                prod = products.get_product_by_id(prod_id)
                cantidad = item[2]
                detalle_prods.append((prod, cantidad))
        obj['detalle'] = detalle_prods
        detalle.append(obj)

    return render_template('compras.html', user= current_user.get_data(), detalle=detalle)

@app.route('/clusters')
def get_products_by_cluster():
    prods = products.products
    group = request.args.get('g')
    if group is None:
        group = 0
    else:
        group = int(group)
    cluster_labels = get_clusters()
    prods_by_cluster = []
    labels = {label for label in cluster_labels}
    labels = list(labels)
    cluster_name = ''
    for idx, label in enumerate(cluster_labels):
        if label == group:
            prods_by_cluster.append(prods[idx])
    return render_template('clusters.html', prods=prods_by_cluster, groups=labels, group=group)

@app.template_filter('date')
def timestamp_to_date(ts):
    date = datetime.fromtimestamp(ts)
    return date.date()
