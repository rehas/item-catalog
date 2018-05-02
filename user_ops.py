from flask import Flask, request, jsonify, render_template, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Item, Category, Base
from flask import session as login_session

from datetime import datetime

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session  = DBSession()

def registerUser(login_session):
    email = login_session['email']
    existingUser = session.query(User).filter_by(email = email).first()
    if existingUser is not None:
        print("User already in DB => %s") % existingUser.name
        return existingUser
    else:
        newUser = User(email = email)
        newUser.name    = login_session['username']
        newUser.picture = login_session['picture'] 
        newUser.picture = login_session['email']
        session.add(newUser)
        session.commit()
        print("New User succesfully added to DB")
        return newUser