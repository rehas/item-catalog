from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Item, Category, Base

from datetime import datetime
engine = create_engine('sqlite:///itemCatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session  = DBSession()

# Create User 1

if session.query(User).first() is None:
    user = User(name = 'admin')
    user.email = 'admin@admin.admin'

    session.add(user)
    session.commit()
 
# # Create initial categories
#
if session.query(Category).first() is None:
 
    category1 = Category(name = 'Boxing')
    category2 = Category(name = 'Running')
    category3 = Category(name = 'Yoga')
    category4 = Category(name = 'Biking')
    
    session.add_all([category1, category2, category3, category4])
    session.commit()


# Reset initial items

#items_do_delete = session.query(Item).all()

if session.query(Item).first() is not None:
    session.query(Item).delete()

    session.commit()



items = []

for i in [0,1,2,3]:
    items.append( Item(\
    name = 'item_%s' %(i+1) , \
    description = 'description_%s' %(i+1), \
    category_id = i+1, \
    created_by = 1, \
    last_edit = datetime.now()))

session.add_all(items)
session.commit()
