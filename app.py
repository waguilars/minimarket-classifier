from flask import Flask, render_template, request
from controllers import products

app = Flask(__name__)


@app.route('/')
def index():
    prods = products.get_last_products()
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
    return render_template('category.html', category=category, sub_category=param,sub_cats=sub_cats, prods=prods)



