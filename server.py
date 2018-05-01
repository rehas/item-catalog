from flask import Flask, request, jsonify, render_template, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Item, Category, Base

from datetime import datetime

import oauthbridge

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
        latest_items = session.query(Item).order_by(Item.id.desc()).limit(5)
        return render_template('index.html', categories = categories, latest_items = latest_items, user = request.args.get('user'))
    if request.method == 'POST':
        newCategory = Category(name = request.form['newCategoryName'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('catalog'))



@app.route('/catalog/<string:category_name>/items', methods = ['GET', 'POST'])
def categoryItems(category_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        selected_category_id = session.query(Category).filter_by(name = category_name).first().id
        category_items = session.query(Item).filter_by(category_id = selected_category_id).order_by(Item.name).all()        
        return render_template('category-items.html', categories = categories, category_name = category_name, category_items = category_items)
    if request.method == 'POST':
        category_id_for_item = session.query(Category).filter_by(name = category_name).first().id
        newItem = Item(name = request.form['newItemName'],
        description = request.form['newItemDescription'])
        newItem.category_id = category_id_for_item
        newItem.created_by = 1 # TODO : make it the actual signed in user
        newItem.last_edit = datetime.now()
        session.add(newItem)
        session.commit()

        return redirect(url_for('categoryItems', category_name = category_name))


@app.route('/catalog/<string:category_name>/<string:item_name>', methods = ['GET', 'POST'])
def singleItem(category_name, item_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        selected_category_id = session.query(Category).filter_by(name = category_name).first().id
        category_items = session.query(Item).filter_by(category_id = selected_category_id).order_by(Item.name).all()
        selected_item = session.query(Item).filter_by(name = item_name).first()
        return render_template('item-detail.html', categories = categories, category_name = category_name, category_items = category_items, item_name = item_name, selected_item = selected_item)        
    if request.method == 'POST':
        selected_category_id = session.query(Category).filter_by(name = category_name).first().id
        editItem = session.query(Item).filter_by(category_id = selected_category_id).filter_by(name = item_name).first()
        editItem.name = request.form['editItemName']
        editItem.description = request.form['editItemDescription']
        session.add(editItem)
        session.commit()
        return redirect(url_for('categoryItems', category_name = category_name))
    
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods = ['POST'])
def deleteSingleItem(category_name, item_name):
    if request.method == 'GET':
        return # Todo => redirect to somehwere logical
    if request.method == 'POST':
        deleteItem = session.query(Item).filter_by(name = item_name).first()
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('categoryItems', category_name = category_name))


@app.route('/login/<string:provider>', methods = ['GET', 'POST'])
def login(provider):
    if request.method == 'GET':
        oauthbridge.testBridge(provider, request)
        state  = oauthbridge.showLogin()
        return render_template('login.html', STATE = state)
    if request.method == 'POST':
        if provider == 'google':
            login_session =  oauthbridge.gConnect(request)
            print("here in login/google/post")
            print(login_session)
            # return "you're trying to login with %s" % provider
            return redirect( url_for( 'catalog', user = login_session['username']))
        if provider == 'facebook':
            return "you're trying to login with %s" % provider


@app.route('/logout/<string:provider>', methods = ['GET', 'POST'])
def logout(provider):
    return "you're logging out from %s" % provider            


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    
    app.run(host = '0.0.0.0', port = 8000)


