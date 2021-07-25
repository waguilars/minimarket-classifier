import csv

from flask.json import dump

products = []

with open('data.csv', mode='r', encoding='utf-8-sig') as data:
    reader = csv.DictReader(data, delimiter=';')
    for row in reader:
        products.append(row)

def get_last_products():
    prods =products[-50:] 
    prods = [p for p in prods if int(p['STOCK']) > 0]
    return prods[-12:]

def get_product_by_id(id):
    for prod in products:
        if int(prod['ID']) == id:
            return prod
    return None

def get_products_by_category(category):
    prods = [prod for prod in products if prod['CATEGORY'] == category and int(prod['STOCK']) > 0]
    return prods

def get_products_by_sub_category(sub_category):
    print(sub_category)
    prods = [prod for prod in products if prod['SUB CATEGORY'] == sub_category and int(prod['STOCK']) > 0]
    return prods


def get_sub_categories(category):
    sub_cats = { prod['SUB CATEGORY'] for prod in products if prod['CATEGORY'] == category  }
    return list(sub_cats)


def get_categories():
    categories = {prod['CATEGORY'] for prod in products}
    return list(categories)