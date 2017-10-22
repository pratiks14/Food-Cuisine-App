from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Cuisine, FoodItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
engine = create_engine("sqlite:///foodcuisine.db")

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

@app.route('/signup',methods=['POST'])
def signup():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['content-type'] = 'application/json'
		return response
	params = json.loads(request.data)
	login_session['username'] = params['username']
	login_session['email']  = params['email']+'@food.com'
	login_session['picture'] = 'http://i63.tinypic.com/3495pax.png'
	login_session['provider'] = 'default'
	login_session['password'] = params['password']
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 200px; height: 200px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output

@app.route('/login',methods =['POST'])
def login():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("invalid state parameter"),401)
		response.headers['content-type'] = 'application/json'
		return response

	params = json.loads(request.data)
	email = params['email']+'@food.com'
	password = params['password']
	if validateUser(email,password):
		user_id = getUserID(email)
		user = getUserInfo(user_id)
		login_session['username'] = user.name
		login_session['email']  = user.email
		login_session['picture'] = user.picture
		login_session['provider'] = 'default'
		login_session['password'] = user.password
		login_session['user_id'] = user_id
		output = ''
		output += '<h1>Welcome, '
		output += login_session['username']
		output += '!</h1>'
		output += '<img src="'
		output += login_session['picture']
		output += ' " style = "width: 200px; height: 200px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
		flash("you are now logged in as %s" % login_session['username'])
		return output
	else:
		response = make_response(json.dumps('Invalid credentials'),200)
		response.headers['content-type'] = 'application/json'
		return response	


@app.route('/gconnect', methods=['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['content-type'] = 'application/json'
		return response
	code = request.data
	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)

	except FlowExchangeError as e:
		response = make_response('failed to upgrade the authorization code'+str(e), 401)
		response.headers['content-type'] = 'application/json'
		return response
	# check that the access token is valid
	access_token = credentials.access_token
	url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token

	h = httplib2.Http()
	response = h.request(url, 'GET')[1]
	str_response = response.decode('utf-8')
	result = json.loads(str_response)

	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response    

	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response	
	
	# Store the access token in the session for later use.
	login_session['access_token'] = access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	login_session['provider'] = "google"
	
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output


def createUser(login_session):
	if login_session['provider'] == 'default':
		newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'],password=login_session['password'])
	else:
		newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id


def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user


def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

def validateUser(email,password):
	user_id = getUserID(email)
	if user_id is not None:
		user = getUserInfo(user_id)
		if user.password != password:
			return False
		return True	
	return False		



@app.route('/disconnect')
def disconnect():
	try :
		if login_session['provider'] == 'default' :
			del login_session['username']
			del login_session['email']
			del login_session['picture']
			del login_session['provider']
			response = make_response(json.dumps("Successfully disconnected!!"),200)	
			response.headers['content-type'] = 'application/json'
			return response		

		else:
			access_token = login_session.get('access_token')#return none instead of an err if key not present
			if access_token == None:
				response = make_response(json.dumps("user not logged IN!!"),400)
				response.headers['content-type'] = 'application/json'
				return response
			# if login_session.get('provider') == 'google':
			url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
			h = httplib2.Http()
			result = h.request(url,'GET')[0]
			print result
			if result['status'] == '200':
				del login_session['access_token']
				del login_session['gplus_id']
				del login_session['username']
				del login_session['email']
				del login_session['picture']
				del login_session['provider']
				response = make_response(json.dumps("Successfully disconnected!!"),200)	
				response.headers['content-type'] = 'application/json'
				return response
			else:
				response = make_response(json.dumps("failed to disconnect"),400)
				response.headers['content-type'] = 'content-type'
				return response
	except :
		flash("Already logged Out!!")
		return redirect(url_for('showCuisines'))		


@app.route('/')
@app.route('/cuisines')
def showCuisines():
	cuisines = session.query(Cuisine).order_by(asc(Cuisine.name))
	user_id = getUserID(login_session.get('email'))	
	if not user_id:
		flash("User Must login")
	return render_template('cuisine.html',cuisines=	cuisines,user_id=user_id)


@app.route('/fooditem/<int:cuisine_id>')
def showItems(cuisine_id):
	foodItems =session.query(FoodItem).filter_by(cuisine_id=cuisine_id).all()
	user_id = getUserID(login_session.get('email'))	
	if not user_id:
		flash("User Must login")
	return render_template('fooditems.html',foodItems=foodItems,cuisine_id=cuisine_id)

@app.route('/addcuisine' , methods=['GET','POST'])
def addCuisine():
	user_id = getUserID(login_session.get('email'))	
	if not user_id:
		flash("User Must login")
		return redirect(url_for('showCuisines'))
	if request.method == 'POST':
		user_id = getUserID(login_session['email'])
		cuisine1 = Cuisine(user_id=user_id,name=request.form['name'])
		session.add(cuisine1)
		session.commit()
		flash("another cuisine added")
		return redirect(url_for('showCuisines'))
	else:
		return render_template('cuisineform.html')

@app.route('/deletecuisine/<int:cuisine_id>')
def deleteCuisine(cuisine_id):
	user_id = getUserID(login_session.get('email'))	
	if not user_id:
		flash("User Must login")
		return redirect(url_for('showCuisines'))
	delcuisine=session.query(Cuisine).filter_by(id = cuisine_id).one()
	session.delete(delcuisine)
	session.commit()
	flash("its deleted!! to add again click on add")
	return redirect(url_for('showCuisines'))

@app.route('/item/<int:cuisine_id>/<int:item_id>')
def itemDetail(cuisine_id,item_id):
	user_id = getUserID(login_session.get('email'))
	foodItem = session.query(FoodItem).filter_by(id = item_id,cuisine_id = cuisine_id).one()
	creater = session.query(User).filter_by(id = foodItem.user_id).one()
	return render_template('item.html',user_id=user_id,creater = creater,foodItem=foodItem)

@app.route('/additem/<int:cuisine_id>',methods = ['GET','POST'])
def addFoodItem(cuisine_id):
	user_id = getUserID(login_session.get('email'))
	if not user_id:
		flash("User Must login")
		return redirect(url_for('showItems',cuisine_id= cuisine_id))
	if request.method == 'POST':
		foodItem = FoodItem(user_id=user_id,description=request.form['description'],name = request.form['name'],ingredient = request.form['ingredient'],cuisine_id=cuisine_id)
		session.add(foodItem)
		session.commit()
		flash("A food item added to Cuisine")
		return redirect(url_for('showItems',cuisine_id=cuisine_id))
	else:
		return render_template('addfooditem.html')

@app.route('/deleteitem/<int:cuisine_id>/<int:item_id>')
def deleteFoodItem(cuisine_id,item_id):
	user_id = getUserID(login_session.get('email'))
	if not user_id:
		flash("User Must login")
		return redirect(url_for('showItems',cuisine_id= cuisine_id))
	delItem = session.query(FoodItem).filter_by(id = item_id).one()
	session.delete(delItem)
	session.commit()
	flash("Food Item deleted")
	return redirect(url_for('showItems',cuisine_id=cuisine_id))

@app.route('/edititem/<int:item_id>',methods=['GET','POST'])
def editFoodItem(item_id):
	foodItem =session.query(FoodItem).filter_by(id = item_id).one()
	user_id = getUserID(login_session.get('email'))
	if not user_id:
		flash("User Must login")
		return redirect(url_for('showItems',cuisine_id= foodItem.cuisine_id))
	if request.method == 'POST':
		foodItem.description = request.form['description']
		foodItem.name = request.form['name']
		foodItem.ingredient = request.form['ingredient']
		session.commit()
		flash("The food Item is Edited!!")
		return redirect(url_for('showItems',cuisine_id=foodItem.cuisine_id))
	else:
		return render_template('editfooditem.html',foodItem=foodItem)


if __name__ == '__main__':
	app.secret_key = "my_app_secretkey"
	app.debug = True
	app.run(host='0.0.0.0',port=5000)
