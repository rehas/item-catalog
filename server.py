from flask import Flask, request, jsonify, render_template, url_for, redirect

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
@app.route('/catalog', methods = ['GET', 'POST'])
def catalog():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        return


@app.route('/catalog/<string:category_name>/items', methods = ['GET', 'POST'])
def categoryItems(category_name):
    if request.method == 'GET':
        return render_template('category-items.html', category = category_name)
    if request.method == 'POST':
        return "You're now adding items for category named: %s" % category_name


@app.route('/catalog/<string:category_name>/<string:item_name>', methods = ['GET', 'PUT', 'DELETE'])
def singleItem(category_name, item_name):
    if request.method == 'GET':
        return render_template('item-detail.html', category = category_name, item = item_name)        
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


