#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(50), nullable=True)
    picture = Column(String(250))


class Cuisine(Base):

    __tablename__ = 'cuisine'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id',
                                         ondelete='CASCADE'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {'name': self.name, 'id': self.id}


class FoodItem(Base):

    __tablename__ = 'food_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    ingredient = Column(String(250))
    cuisine_id = Column(Integer, ForeignKey('cuisine.id',
                                            ondelete='CASCADE'))
    cuisine = relationship(Cuisine)
    user_id = Column(Integer, ForeignKey('user.id',
                                         ondelete='CASCADE'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'ingredient': self.ingredient,
        }


engine = create_engine('sqlite:///foodcuisine.db')

Base.metadata.create_all(engine)  # similar to create db
