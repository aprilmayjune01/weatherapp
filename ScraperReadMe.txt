
Scraper reads from ->

	https://weather.com/en-GB/weather/today/l/51.48,-3.18?par=google&temp=c

It essentially changes the website url and scrapes the individual page -> 

	/today/l/[lat],[lon]

[lat] and [lon] are values taken from a dictionary of city locations which can reference points on weather.com

I've tried to generate lat and lon from scraping other pages but cannot get it to work, have also tried running Selenium, but every time I try that
each website kicks me since its technically in the same idea as DDOS bot. 
