from sqlalchemy import \
Column, ForeignKey, Integer, String, create_engine, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)
    email = Column(String(100), unique = True)
    picture = Column(String, nullable = True)
    access_token_google = Column(String, nullable = True)
    access_token_github = Column(String, nullable = True)


class Category(Base):
    __tablename__ =  'category'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), unique = True)

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), unique = True)
    description = Column(String, nullable = False)
    last_edit = Column(DateTime, nullable = True)
    created_by = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    user = relationship(User)
    category = relationship(Category)

engine = create_engine('sqlite:///itemCatalog.db')

# User.__table__.drop(engine, checkfirst = True)

Base.metadata.create_all(engine)