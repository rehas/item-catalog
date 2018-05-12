import random
import string
import httplib2
import json
import requests
from flask import Flask, render_template,\
    request, redirect, jsonify, url_for, flash

from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('keys/client_secret.json', 'r').read())['web']['client_id']

GHCLIENT_ID = json.loads(
    open('keys/ghclient_secret.json', 'r').read())['web']['client_id']
GHCLIENT_SCRT = json.loads(
    open('keys/ghclient_secret.json', 'r').read())['web']['client_secret']


def showLogin(login_session):
    """
        Creates a state variable and stores it in the
        login_session before Login
    """
    login_session = login_session
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return login_session


def gConnect(req, login_session):
    """
        Provides a google sign-in process
        Authenticates with google server and gets user information
        after authentication
    """
    login_session = login_session
    request = req
    """
    Tests for DEBUG mode
    print("In gConnect")
    print(request)
    """
    # Checking state of the request with current state of server
    # to make sure the request is made by client, not attacker
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state params'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    # Exchanging code with acess_token
    try:
        oauth_flow = flow_from_clientsecrets(
            'keys/client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to update auth code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Checking to see if there's a server error
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 501)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    # Got the userID, comparing it with token's userID
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps('Tokens user Id doesnt match given user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Checking if our app's clientID matches the token's client ID
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    # Everything seems fine, we can now check if the user is already
    # logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps(
                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # USER LOGGED IN SUCCESFULLY
    # Storing access token and gplus_id in login session
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # GET USER INFO using the access_token
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    """
    Tests for DEBUG mode
    print("Data")
    print(data)
    print("login_session")
    print(login_session)
    """
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    """
    Tests for DEBUG mode
    print("login_session")
    print(login_session)
    """
    return login_session


def ghConnect(req, login_session):
    """
    Github authentication process
    """
    login_session = login_session
    request = req
    """
    Tests for DEBUG mode
    print("In ghConnect")
    print(req)
    print(request.args.get('state'))
    print(login_session['state'])
    """
    # Checking to see the state variable on the server and
    # the client are the same to make sure there's no attack
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state params'), 401)
        response.headers['Content-Type'] = 'application/json'
        print("Error\n %s" % response)
        return login_session
    code = request.args.get('code')
    """
    Tests for DEBUG mode
    print('printing code')
    print(code)
    print("Code from github is : \n")
    print(code)
    """
    # Constructing url to get the access_token from github
    url = "https://github.com/login/oauth/access_token?"
    url += "client_id=%s&client_secret=%s&code=%s&state=%s" % (
        GHCLIENT_ID, GHCLIENT_SCRT, code, login_session['state'])
    """
    Tests for DEBUG mode
    print("url is")
    print(url)
    """
    h = httplib2.Http()
    response, content = h.request(url, 'POST')
    """
    Tests for DEBUG mode
    print("response from GHUB")
    print(content)
    print("access token")
    """
    # Getting access token from github and storing in login session
    login_session['access_token_github'] = content.split(
        '&')[0].replace("access_token=", "")
    """
    Test
    print(login_session['access_token_github'])
    """
    # Constructing url for user information access
    user_info_url = "https://api.github.com/user?access_token"
    user_info_url += "=%s" % login_session['access_token_github']
    user_data = requests.get(user_info_url).json()
    """
    Tests again
    print(user_info_url)
    print("User Info")
    print(user_data)
    """
    # Setting user info into login_session
    login_session['username'] = user_data['login']
    login_session['picture'] = user_data['avatar_url']
    login_session['email'] = user_data['email']
    return login_session


def disconnect(login_session):
    """
    Emptying the login_session object to logout the user
    """
    ls = login_session
    print("Disconnecting")
    for v in ls.keys():
        print(ls[v])
        ls[v] = ""
    """
    Tests for DEBUG mode
    print("printing login session after disconnect")
    print(ls)
    """
    return ls
