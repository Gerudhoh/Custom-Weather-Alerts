import os
import requests, json
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
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

def will_rain_tonight():
    weather = get_weather()
    main_weather = weather['current']['weather'][0]['main']
    if main_weather.casefold() == "rain":
        return True
    return will_rain(weather['hourly'])

def will_rain(hourly_weather):
    for i in range(0, 10):
        hour_forcast = hourly_weather[i]
        pop = hour_forcast['pop']
        # print(pop)
        if pop >= 0.5:
            return True
    return False

def send_email():
    message = Mail(
    from_email='gerudhoh+weather@gmail.com',
    to_emails='gerudhoh@gmail.com',
    subject='Bring the cushions in!',
    content = Content("text/plain", "It's likely to rain tonight! We should probably bring in the cushions"))

    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    
if will_rain_tonight() == True:
    send_email()
else:
    print("No rain!")
