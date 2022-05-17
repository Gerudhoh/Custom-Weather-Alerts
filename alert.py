import os
import requests, json
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, To, Email

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
    for i in range(0, 10):
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


def get_email_content(will_rain_tn, need_ac):
    if will_rain_tn and need_ac:
        return Content("text/plain", "It's likely to rain tonight! We should probably bring in the cushions. Also it'll be stupid hot over the next few days, so let's turn on the A/C")
    elif will_rain_tn and not need_ac:
        return Content("text/plain", "It's likely to rain tonight! We should probably bring in the cushions")
    else:
       return Content("text/plain", "It'll be stupid hot over the next few days, let's turn on the A/C")


def send_email(will_rain_tn, need_ac):
    from_email = Email('gerudhoh+weather@gmail.com')
    to_emails = [To('gerudhoh@gmail.com'), To('choh@rogers.com'), To('paolahoh@rogers.com'), To('barbdowsley@yahoo.ca')]
    subject = 'Semi-Nightly Weather Report'
    content = get_email_content(will_rain_tn, need_ac)
    email = Mail(from_email, to_emails, subject, content)

    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    response = sg.send(email)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    

weather = get_weather()
will_rain_tn = will_rain_tonight(weather)
need_ac = will_need_ac(weather)

if will_rain_tn == False and need_ac == False:
    print("No alert needed!")
else:
    send_email(will_rain_tn, need_ac)
