#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Cuisine, Base, FoodItem, User

engine = create_engine('sqlite:///foodcuisine.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()

# Create dummy user

User1 = User(name='Pratik Shetty', email='pratiks14@food.com',
             picture='''https://pbs.twimg.com/profile_images/
        2671170543/18debd694829ed78203a5a36dd364160_400x400.png''',
             password='pratiks14')
session.add(User1)
session.commit()

# Menu for UrbanBurger

cuisine1 = Cuisine(user_id=1, name='American')

session.add(cuisine1)
session.commit()

foodItem2 = FoodItem(user_id=1, name='Veggie Burger',
                     description='''Juicy grilled veggie patty
                     with tomato mayo and lettuce''',
                     ingredient='veggie patty,tomato',
                     cuisine=cuisine1)

session.add(foodItem2)
session.commit()

foodItem1 = FoodItem(user_id=1, name='French Fries',
                     description='with garlic and parmesan',
                     ingredient='gralic, parmesan', cuisine=cuisine1)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name='Chicken Burger',
                     description='''Juicy grilled chicken patty with
                      tomato mayo and lettuce''',
                     ingredient='chicken patty,tomato',
                     cuisine=cuisine1)

session.add(foodItem2)
session.commit()

foodItem3 = FoodItem(user_id=1, name='Chocolate Cake',
                     description='''fresh baked and served
                      with ice cream''',
                     ingredient='ice cream', cuisine=cuisine1)

session.add(foodItem3)
session.commit()

foodItem4 = FoodItem(user_id=1, name='Sirloin Burger',
                     description='Made with grade A beef',
                     ingredient='beaf,burger', cuisine=cuisine1)

session.add(foodItem4)
session.commit()

foodItem5 = FoodItem(user_id=1, name='Root Beer',
                     description='16oz of refreshing goodness',
                     ingredient='beer', cuisine=cuisine1)

session.add(foodItem5)
session.commit()

foodItem6 = FoodItem(user_id=1, name='Iced Tea',
                     description='with Lemon',
                     ingredient='tea,ice cubes', cuisine=cuisine1)

session.add(foodItem6)
session.commit()

foodItem7 = FoodItem(user_id=1, name='Grilled Cheese Sandwich',
                     description='''On texas toast
                      with American Cheese''',
                     ingredient='bread,cheese', cuisine=cuisine1)

session.add(foodItem7)
session.commit()

# Menu for Super Stir Fry

cuisine2 = Cuisine(user_id=1, name='Indian')

session.add(cuisine2)
session.commit()

foodItem1 = FoodItem(user_id=1, name='Chicken Stir Fry',
                     description='''With your choice of
                     noodles vegetables and sauces''',
                     ingredient='''chicken,onions,
                     garam masala,olive oil''', cuisine=cuisine2)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name='Peking Duck',
                     description=''' A famous duck dish from
                      Beijing[1] that has been prepared since
                       the imperial era. The meat is prized for
                       its thin, crisp skin, with authentic versions
                       of the dish serving mostly the skin
                       and little meat, sliced in front of the
                       diners by the coo''',
                     ingredient='''duck meat,garam masala,garlic,
                     olive oil''', cuisine=cuisine2)

session.add(foodItem2)
session.commit()

print 'added menu items!'
