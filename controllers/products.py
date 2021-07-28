import csv

from flask.json import dump, load

products = []

def load_data():
    with open('data.csv', mode='r', encoding='utf-8-sig') as data:
        reader = csv.DictReader(data, delimiter=';')
        for row in reader:
            products.append(row)

def reset_data():
    products = []


def add_new(category, sub_category, product_name, price, stock, url):
    last_id = int(products[-1]['ID'])
    price = str(price).replace('.', ',')
    row = [last_id+1, category, sub_category, product_name, price, int(stock), url]
    with open('data.csv', mode='a+', encoding='utf-8-sig') as data:
        writer = csv.writer(data, delimiter=';')
        writer.writerow(row)
    reset_data()
    load_data()


def get_last_products():
    prods = products[-50:]
    prods = [p for p in prods if int(p['STOCK']) > 0]
    return prods[-12:]


def get_product_by_id(id):
    for prod in products:
        if int(prod['ID']) == id:
            return prod
    return None


def get_products_by_category(category):
    prods = [prod for prod in products if prod['CATEGORY']
             == category and int(prod['STOCK']) > 0]
    return prods


def get_products_by_sub_category(sub_category):
    print(sub_category)
    prods = [prod for prod in products if prod['SUB CATEGORY']
             == sub_category and int(prod['STOCK']) > 0]
    return prods


def get_sub_categories(category):
    sub_cats = {prod['SUB CATEGORY']
                for prod in products if prod['CATEGORY'] == category}
    return list(sub_cats)


def get_categories():
    categories = {prod['CATEGORY'] for prod in products}
    return list(categories)
