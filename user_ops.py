from flask import Flask, request, jsonify, render_template, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Item, Category, Base
from flask import session as login_session

from datetime import datetime

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def registerUser(login_session):
    """
    Constructs User object from login_session
    Checks if the user exists, if so returns User
    If not, creates a new user with login_session data
    """
    ls = login_session
    """
    Console tests for DEBUG
    print("in registerUser")
    print(ls)
    """
    email = ls['email']
    existingUser = session.query(User).filter_by(email=email).first()
    if existingUser is not None:
        # Console test
        # print("User already in DB => %s") % existingUser.name
        return existingUser
    else:
        newUser = User(email=email)
        newUser.name = ls['username']
        newUser.picture = ls['picture']

        if login_session['access_token']:
            newUser.access_token_google = ls['access_token']
        elif login_session['access_token_github']:
            newUser.access_token_github = ls['access_token_github']
        else:
            # console log
            print("No Access token from SignIn attempt found!")

        session.add(newUser)
        session.commit()
        # console log
        # print("New User succesfully added to DB")
        return newUser
