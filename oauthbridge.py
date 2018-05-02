from flask import Flask, render_template, request, redirect,jsonify, url_for, flash

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('keys/client_secret.json', 'r').read())['web']['client_id']

def testBridge(*args):
    print("We're in oauthbridge.py file")
    print(args[0])
    print(args[1])

def getSession():
    return login_session

def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return login_session['state']


def gConnect(req):
    request = req
    print("In gConnect")
    print (request)
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state params'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('keys/client_secret.json', scope ='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to updare auth code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 501)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Tokens user Id doesnt match given user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        #return response
    
    # USER LOGGED IN SUCCESFULLY

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # GET USER INFO

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print("Data")
    print(data)
    print("login_session")
    print(login_session)
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    print("login_session")
    print(login_session)

    # user_id = getUserId(login_session['email'])
    #if user_id == None:
    #    user_id = createUser(login_session)
    # login_session['user_id'] = user_id

    return login_session
    # return render_template('/index.html', user = login_session['username'])

def fbConnect(req):
    request = req
    print("In fbConnect")
    print(req)

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state params'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    print("code")
    print(code)