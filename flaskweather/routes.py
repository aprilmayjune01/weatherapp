import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskweather import app, db, bcrypt
from flaskweather.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskweather.models import User
from flask_login import login_user, current_user, logout_user, login_required
from bs4 import BeautifulSoup
import requests

global locationCityName
locationCityName = "Cardiff"

global tempRaw
global time
global location
global phrase
global chosenStyle 
chosenStyle = "Both"

@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash ('Your account has successfully been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_picture', picture_fn)
    form_picture.save(picture_path)

    return picture_fn



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has successfully been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_picture/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def template(text = ""):
    templateDate = {
        'text' : text,
        'tvalues' : (" ","Cardiff", "York", "Portsmouth","Swansea","Manchester","London","Leeds","Sheffield",
            "Bradford","Liverpool","Bristol","Sunderland","Edinburgh","Exeter","Dublin"),
        'selected_tvalue' : "unselected. Please select a city."
    }
    return templateDate


@app.route("/location", methods=['POST', 'GET'])
def location():
    tvalue= "unselected. Please select a city."
    if request.method == "POST":            
        tvalue = str(request.form['tvalue'])

    global locationCityName
    locationCityName = tvalue

    templateData = template(text = tvalue)
    templateData['selected_tvalue'] = tvalue 

    if locationCityName == ' ':
        locationCityName = "Cardiff"
        templateData = template(text = locationCityName)
        templateData['selected_tvalue'] = locationCityName
    return render_template('dropdown.html',**templateData)

    if tvalue == 'unselected. Please select a city.':
        locationCityName = "Cardiff"
        templateData = template(text = locationCityName)
        templateData['selected_tvalue'] = locationCityName

    return render_template('dropdown.html',**templateData)

    return render_template('dropdown.html', **templateData)

@app.route('/result/')
def result():

    locations = {
            'Cardiff': {'lati':51.48,'longi':-3.18},
            'York': {'lati':54.00,'longi':-1.08},
            'Portsmouth': {'lati':50.82,'longi':-1.09},
            'Swansea': {'lati':51.62,'longi':-3.94},
            'Manchester': {'lati':53.48,'longi':-2.24},
            'London': {'lati':51.48,'longi':0},
            'Leeds':{'lati':53.80,'longi':-1.55},
            'Sheffield':{'lati':53.40,'longi':-1.47},
            'Bradford':{'lati':53.80,'longi':-1.76},
            'Liverpool':{'lati':53.40,'longi':-2.98},
            'Bristol':{'lati':51.45,'longi':-2.59},
            'Sunderland':{'lati':54.90,'longi':-1.38},
            'Edinburgh':{'lati':55.95,'longi':-3.19},
            'Exeter':{'lati':50.72,'longi':-3.53 },
            'Dublin':{'lati':53.34,'longi':-6.26},                  
            }

    global locationCityName
    searchCity = str(locationCityName)

    try:
        lat = str(locations[searchCity].get('lati'))
    except KeyError:
        lat = "51.48"

    try:
        lon = str(locations[searchCity].get('longi'))
    except KeyError:
        lon = "-3.18"

    weatherUrl=('https://weather.com/en-GB/weather/today/l/'+lat+','+lon+'?par=google&temp=c')

    source = requests.get(weatherUrl).text

    soup = BeautifulSoup(source, 'lxml')

    global tempRaw
    global time
    global location
    global phrase

    tempRaw = soup.find("div",{"class" : "today_nowcard-temp"}).text
    time = soup.find('body').select_one('p').text
    location = soup.find('body').select_one('h1').text
    phrase = soup.find("div",{"class" : "today_nowcard-phrase"}).text

    return render_template('weatherLocation.html',tempOut = tempRaw, cityOut = "in " + location + " " + time, phraseOut = phrase)


@app.route('/settings/', methods= ['POST','GET'])
def settings():

    if request.method == 'POST':
        global chosenStyle
        chosenStyle = request.form["options"]

    return render_template("settings.html", chosenStyleOut = chosenStyle)


@app.route('/outfit/')
def outfit():

    global tempRaw
    global time
    global location
    global phrase
    global chosenStyle

    outfits = {
        'Sunny': {'male':'T-shirt and Shorts, Sunglasses, Trainers','female':'Summer Dress, Sunglasses, Sandals'},
        'Cloudy': {'male':'T-shirt and Jeans, Denim Jacket, Sunglasses, Trainers','female':'T-shirt and Skirt, Denim Jacket, Sunglasses, Trainers'},
        'Rainy': {'male':'T-shirt and Jeans, Waterproof shoes, Raincoat, Umbrella','female':'Cardigan and Jeans, Waterproof shoes, Raincoat, Umbrella'},
        'Fog': {'male':'Cardigan and Jeans, Shoes, Raincoat','female':'Cardigan and Jeans, Shoes, Raincoat'},
        'Thunderstorms': {'male':'T-shirt and Jeans, Waterproof shoes, Raincoat, Umbrella','female':'Cardigan and Jeans, Waterproof shoes, Raincoat, Umbrella'}, 
        'Partly Cloudy': {'male':'long-sleeve T-shirt and Jeans, Sweater, Scarf','female':'long-sleeve T-shirt and Jeans, Sweater, Scarf'},
        'Fair': {'male':'T-shirt, Jeans, Sunglasses, Trainers','female':'Summer Dress, Sunglasses, Trainers'},                 
    }

    maleOutfit = ""
    femaleOutfit = ""

    maleOutfit = str(outfits[phrase].get('male'))
    femaleOutfit = str(outfits[phrase].get('female'))

    if chosenStyle == "Male":
        allOutfit = maleOutfit
    elif chosenStyle == "Female":
        allOutfit = femaleOutfit
    elif chosenStyle == "Both":
        allOutfit = maleOutfit + " | " + femaleOutfit

    return render_template("display.html", phraseOut = phrase, outfitOut = allOutfit, styleOut = chosenStyle, locationOut = location)