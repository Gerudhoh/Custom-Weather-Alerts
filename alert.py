import os
import requests, json
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

load_dotenv()

def get_weather():
    LATITUDE = "43.511871"
    LONGITUDE = "-80.192574"
    ow = os.getenv('OPENWEATHER_API_KEY')
    base_url = "http://api.openweathermap.org/data/2.5/onecall?"
    lat = "lat=" + LATITUDE
    lon = "&lon=" + LONGITUDE
    api = "&appid=" + ow
    units = "&units=metric"
    req = base_url + lat + lon + api + units
    response = requests.get(req)
    return response.json()

def send_email():
    message = Mail(
    from_email='gerudhoh+weather@gmail.com',
    to_emails='gerudhoh@gmail.com',
    subject='Weather Alert!',
    html_content='<strong>Alert</strong>')

    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    sg.send(message)
    
weather = get_weather()

current_DT = datetime.fromtimestamp(int(weather['current']['dt']))
print(weather)