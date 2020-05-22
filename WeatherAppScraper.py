from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

locations = {
			1: {'City': 'Cardiff','Latitude':'51.48','Longitude':'-3.18'},
			2: {'City': 'London','Latitude':'51.51','Longitude':'0.13'},
			3: {'City': 'York','Latitude':'54.00','Longitude':'-1.08'},
			4: {'City': 'Portsmouth','Latitude':'50.80','Longitude':'-1.09'},
			5: {'City': 'Swansea','Latitude':'51.62','Longitude':'-3.94'},					
			}

lat=(locations[4]['Latitude'])
lon=(locations[4]['Longitude'])

weatherUrl=('https://weather.com/en-GB/weather/today/l/'+lat+','+lon+'?par=google&temp=c')

source = requests.get(weatherUrl).text

soup = BeautifulSoup(source, 'lxml')

tempRaw = soup.find("div",{"class" : "today_nowcard-temp"}).text
time = soup.find('body').select_one('p').text
location = soup.find('body').select_one('h1').text

print(tempRaw)
print(time)
print(location)

from flask import Flask
app = Flask(__name__)

@app.route('/')

def index():

	return render_template('index.html',text2 = tempRaw, text = "in " + location + " " + time)

################

#@app.route('/')
#def index():
#   return render_template('index.html')

#@app.route('/result',methods = ['POST', 'GET'])
#def result():
#   if request.method == 'POST':
#      result = request.form
#      return render_template("result.html",result = result)

##############

if __name__ == "__main__":
		app.run(debug=True)
		app.run(host = '0.0.0.0', port = 5000)