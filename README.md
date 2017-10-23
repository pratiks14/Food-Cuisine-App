# FoodCusine Catalog #

## Requirements ##

- [Flask](http://flask.pocoo.org)
- [SQLAlchemy](http://www.sqlalchemy.org)
- and [Flask](https://pythonhosted.org/Flask

##Dependencies ##
Run the following commands:

    pip2 install flask packaging oauth2client redis passlib flask-httpauth
    pip2 install sqlalchemy flask-sqlalchemy psycopg2 bleach requests


## Run the app ##

To start the app simply run

	python project.py

The app is configured to run on port:**5000**

## Remarks ##
- The app uses Bootstrap and is responsive.
- The pictures are stored in the database.
- The app offers 3 JSON API endpoints:
	-  /cuisine/JSON
	-  /cuisine/cuisine_id/JSON
    -  /cuisine/cuisine_id/item/item_id/JSON


## How to use the App ##

- If not logged in you have to log in
- The app provides its own authorization and also through 3rd party google login authentication and authorization.
- The app also alowes its user to signUP.
- After you login you can view the existing cuisines that are stored in the database.
- you can also add your own cuisine that arent on the given list.**(only if logged in)**
- When you click on any of the cusines, you are taken another page where fooditem are listed belonging to that cuisine.
- You can add your own food item to that list.
- When you click on any of the items you are taken another page where there is brief description and related Information.
- **To delete or edit a fooditem or delete an cuisine You have to be the user who added it.**
