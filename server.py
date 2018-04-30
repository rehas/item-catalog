from flask import Flask, request, jsonify, render_template, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Item, Category, Base

from datetime import datetime

app = Flask(__name__)

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session  = DBSession()


@app.route('/', methods = ['GET', 'POST'])
@app.route('/catalog', methods = ['GET', 'POST'])
def catalog():
    if request.method == 'GET':
        categories = session.query(Category).all()
        latest_items = session.query(Item).order_by(Item.id.desc()).limit(2)
        return render_template('index.html', categories = categories, latest_items = latest_items)
    if request.method == 'POST':
        return


@app.route('/catalog/<string:category_name>/items', methods = ['GET', 'POST'])
def categoryItems(category_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        selected_category_id = session.query(Category).filter_by(name = category_name).first().id
        category_items = session.query(Item).filter_by(category_id = selected_category_id).order_by(Item.name).all()        
        return render_template('category-items.html', categories = categories, category_name = category_name, category_items = category_items)
    if request.method == 'POST':
        return "You're now adding items for category named: %s" % category_name


@app.route('/catalog/<string:category_name>/<string:item_name>', methods = ['GET', 'PUT', 'DELETE'])
def singleItem(category_name, item_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        selected_category_id = session.query(Category).filter_by(name = category_name).first().id
        category_items = session.query(Item).filter_by(category_id = selected_category_id).order_by(Item.name).all()
        selected_item = session.query(Item).filter_by(name = item_name).first()
        return render_template('item-detail.html', categories = categories, category_name = category_name, category_items = category_items, item_name = item_name, selected_item = selected_item)        
    if request.method == 'PUT':
        return "You want to edit information of item : %s of category %s" % (item_name, category_name)        
    if request.method == 'DELETE':
        return "You want to delete information of item : %s of category %s" % (item_name, category_name)        


@app.route('/login/<string:provider>', methods = ['GET', 'POST'])
def login(provider):
    if request.method == 'GET':
        return "You're seeing login page for all providers"
    if request.method == 'POST':
        if provider == 'google':
            return "you're trying to login with %s" % provider
        if provider == 'facebook':
            return "you're trying to login with %s" % provider


@app.route('/logout/<string:provider>', methods = ['GET', 'POST'])
def logout(provider):
    return "you're logging out from %s" % provider            
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)


