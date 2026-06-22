import requests
import json

url = 'http://127.0.0.1:5000/api/predict'
files = {'image': open('Frontend/Image 1.jpeg', 'rb')}
try:
    r = requests.post(url, files=files)
    print("Status:", r.status_code)
    print("Response:", json.dumps(r.json(), indent=2))
except Exception as e:
    print("Error:", e)
