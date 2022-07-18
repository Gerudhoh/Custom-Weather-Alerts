import os
import requests, json, time
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, To, Email
from datetime import date, timedelta

load_dotenv()

def get_weather():
    LATITUDE = "43.511871"
    LONGITUDE = "-80.192574"
    ow = os.environ['OPENWEATHER_API_KEY']
    base_url = "http://api.openweathermap.org/data/2.5/onecall?"
    lat = "lat=" + LATITUDE
    lon = "&lon=" + LONGITUDE
    api = "&appid=" + ow
    units = "&units=metric"
    req = base_url + lat + lon + api + units
    response = requests.get(req)
    return response.json()

def will_rain_tonight(weather):
    main_weather = weather['current']['weather'][0]['main']
    if main_weather.casefold() == "rain":
        return True
    return will_rain(weather['hourly'])

def will_rain(hourly_weather):
    for i in range(0, 14):
        hour_forcast = hourly_weather[i]
        pop = hour_forcast['pop']
        if pop >= 0.5:
            return True
    return False

def will_need_ac(weather):
    TEMP_MAX = 25

    if int(weather['current']['feels_like']) < TEMP_MAX:
        return False
    
    daily_weather = weather['daily']
    for i in range(0, 3):
        night_feel = daily_weather[i]['feels_like']['night']
        # If we only have to suffer the heat for one or two nights, we don't need AC
        if int(night_feel) < TEMP_MAX:
            return False
    
    return True

def ac_already_on():
    yesterday_dt = date.today() - timedelta(days = 1)
    yesterday_unix = int(time.mktime(yesterday_dt.timetuple()))
    
    LATITUDE = "43.511871"
    LONGITUDE = "-80.192574"
    ow = os.environ['OPENWEATHER_API_KEY']
    base_url = "http://api.openweathermap.org/data/2.5/onecall/timemachine?"
    lat = "lat=" + LATITUDE
    lon = "&lon=" + LONGITUDE
    dt = "&dt=" + str(yesterday_unix)
    api = "&appid=" + ow
    units = "&units=metric"
    req = base_url + lat + lon + dt + api + units

    response = requests.get(req)
    yesterday_weather = response.json()
    return will_need_ac(yesterday_weather)


def get_email_content(will_rain_tn, turn_ac_on, turn_ac_off):
    message = ""

    if will_rain_tn:
        message += "It's likely to rain tonight! We should probably bring in the cushions. "
    
    if turn_ac_on:
        message += "It'll be stupid hot over the next few days/nights, we might want to turn on the A/C. "
    
    if turn_ac_off:
        message += "It's probably safe to turn off the A/C. "
    
    return Content("text/plain", message)


def send_email(will_rain_tn, turn_ac_on, turn_ac_off):
    from_email = Email('gerudhoh+weather@gmail.com')
    to_emails = [To('gerudhoh@gmail.com'), To('choh@rogers.com'), To('paolahoh@rogers.com'), To('barbdowsley@yahoo.ca')]
    subject = 'Semi-Nightly Weather Report'
    content = get_email_content(will_rain_tn, turn_ac_on, turn_ac_off)
    email = Mail(from_email, to_emails, subject, content)

    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    response = sg.send(email)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    

weather = get_weather()

# Get Cushions Alert
will_rain_tn = will_rain_tonight(weather)

# # Get A/C Alert
# need_ac = will_need_ac(weather)
# ac_is_on = ac_already_on()
# turn_ac_on = need_ac and not ac_is_on
# turn_ac_off = not need_ac and ac_is_on

turn_ac_on = False
turn_ac_off = False

if will_rain_tn == False and turn_ac_on == False and turn_ac_off == False:
    print("No alert needed!")
else:
    send_email(will_rain_tn, turn_ac_on, turn_ac_off)
