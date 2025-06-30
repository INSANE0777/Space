import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")
lat = 28.572872
lon = -80.648980

url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
response = requests.get(url)

print(f"Status: {response.status_code}")
print("Response JSON:", response.json())
