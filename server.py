from flask import Flask, request, jsonify, render_template, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Item, Category, Base
from flask import session as login_session

from datetime import datetime

import oauthbridge
import user_ops

app = Flask(__name__)

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


login_session = {
    "username": "",
    "email": "",
    "picture": "",
    "user_id": "",
    "access_token": "",
    "gplus_id": "",
    "state": "",
    "access_token_github": ""
}


@app.route('/', methods=['GET', 'POST'])
@app.route('/catalog', methods=['GET', 'POST'])
def catalog(user="", STATE=""):
    if request.method == 'GET':
        categories = session.query(Category).all()
        latest_items = session.query(Item).order_by(Item.id.desc()).limit(5)
        global login_session
        print('In catalog\n\n')
        print("login session is : \n")
        print(login_session)
        print("login_session['username] is : \n")
        print(login_session['username'])
        return render_template(
            'index.html', categories=categories, latest_items=latest_items,
            user=login_session['username'], userID=login_session['user_id'])
    if request.method == 'POST':
        newCategory = Category(name=request.form['newCategoryName'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('catalog'))


@app.route('/catalog/<string:category_name>/items', methods=['GET', 'POST'])
def categoryItems(category_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        selected_category_id = session.query(
            Category).filter_by(name=category_name).first().id
        category_items = session.query(
            Item).filter_by(category_id=selected_category_id).order_by(
                Item.name).all()
        return render_template(
            'category-items.html', categories=categories,
            category_name=category_name,
            category_items=category_items,
            user=login_session['username'],
            userID=login_session['user_id'])
    if request.method == 'POST':
        category_id_for_item = session.query(
            Category).filter_by(name=category_name).first().id
        newItem = Item(
            name=request.form['newItemName'],
            description=request.form['newItemDescription'])
        newItem.category_id = category_id_for_item
        userId = session.query(
            User).filter_by(email=login_session['email']).first().id
        newItem.created_by = userId  # DONE : make it the actual signed in user
        newItem.last_edit = datetime.now()
        session.add(newItem)
        session.commit()

        return redirect(url_for('categoryItems', category_name=category_name))


@app.route(
    '/catalog/<string:category_name>/<string:item_name>',
    methods=['GET', 'POST'])
def singleItem(category_name, item_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        selected_category_id = session.query(
            Category).filter_by(name=category_name).first().id
        category_items = session.query(Item).filter_by(
            category_id=selected_category_id).order_by(Item.name).all()
        selected_item = session.query(Item).filter_by(name=item_name).first()
        return render_template(
            'item-detail.html',
            categories=categories,
            category_name=category_name,
            category_items=category_items,
            item_name=item_name,
            selected_item=selected_item,
            user=login_session['username'],
            userID=login_session['user_id'])
    if request.method == 'POST':
        selected_category_id = session.query(
            Category).filter_by(name=category_name).first().id
        editItem = session.query(
            Item).filter_by(
                category_id=selected_category_id).filter_by(
                name=item_name).first()
        editItem.name = request.form['editItemName']
        editItem.description = request.form['editItemDescription']
        session.add(editItem)
        session.commit()
        return redirect(url_for(
            'categoryItems', category_name=category_name))


@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['POST'])
def deleteSingleItem(category_name, item_name):
    deleteItem = session.query(Item).filter_by(name=item_name).first()
    session.delete(deleteItem)
    session.commit()
    return redirect(url_for('categoryItems', category_name=category_name))


@app.route('/pick-provider')
def pickProvider():
    return render_template('pick-login-provider.html')


@app.route('/login/<string:provider>', methods=['GET', 'POST'])
def login(provider):
    if request.method == 'GET':
        if provider == 'google':
            oauthbridge.testBridge(provider, request)
            # login_session = oauthbridge.getSession()
            global login_session
            login_session = oauthbridge.showLogin(login_session)
            return render_template('login-google.html',
                                   STATE=login_session['state'])
        if provider == 'facebook':
            login_session = oauthbridge.getSession()
            login_session['state'] = oauthbridge.showLogin()
            return render_template('login-facebook.html',
                                   STATE=login_session['state'])
        if provider == 'github':
            print("Github Request Printing")
            print(request.args.get('code'))
            if request.args.get('code'):
                global login_session
                login_session = oauthbridge.ghConnect(request, login_session)
                print("login session @ ghconnect after code arrived")
                print(login_session)
                user = user_ops.registerUser(login_session)
                login_session['user_id'] = user.id
                return redirect(url_for(
                    'catalog',
                    user=login_session['username'],
                    STATE=login_session['state']))
            else:
                # login_session = oauthbridge.getSession()
                global login_session
                login_session = oauthbridge.showLogin(login_session)
                return render_template('login-github.html',
                                       STATE=login_session['state'])
    if request.method == 'POST':
        if provider == 'google':
            global login_session
            login_session = oauthbridge.gConnect(request, login_session)
            print("here in login/google/post")
            print(login_session)
            print("\n\n\n\n -----------------")
            print(login_session['username'])
            user = user_ops.registerUser(login_session)
            login_session['user_id'] = user.id
            # return "you're trying to login with %s" % provider
            return redirect(url_for(
                'catalog',
                user=login_session['username'],
                STATE=login_session['state']))
        if provider == 'facebook':
            login_session = oauthbridge.fbConnect(request)
            return "you're trying to login with %s" % provider
        if provider == 'github':
            global login_session
            login_session = oauthbridge.ghConnect(request, login_session)
            print("here in login/github/post")
            print(login_session)
            user = user_ops.registerUser(login_session)
            return redirect(url_for(
                'catalog',
                user=login_session['username'],
                STATE=login_session['state']))


@app.route('/logout')
def logout():
    global login_session
    login_session = oauthbridge.disconnect(login_session)
    return redirect(url_for('catalog'))


@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Category).all()
    return jsonify(category=[c.serialize for c in catalog])


@app.route('/catalog/<string:category_name>/JSON')
def categoryItemsJSON(category_name):
        selected_category_id = session.query(
            Category).filter_by(name=category_name).first().id
        category_items = session.query(
            Item).filter_by(category_id=selected_category_id).order_by(
                Item.name).all()
        return jsonify(categoryItem=[ci.serialize for ci in category_items])


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
