from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
@app.route('/catalog', methods = ['GET', 'POST'])
def catalog():
    if request.method == 'GET':
        return "You have reached the main page my friendss"
    if request.method == 'POST':
        return
@app.route('/catalog/<string:category_name>/items', methods = ['GET', 'POST'])
def categoryItems(category_name):
    if request.method == 'GET':
        return "You're now seeing items for category named: %s" % category_name
    if request.method == 'POST':
        return "You're now adding items for category named: %s" % category_name
        

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)


