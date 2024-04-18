import config
from boot import connection 
import urequests as requests



url = f"http://{config.SERVER}:{config.PORT}{config.ENDPOINT}"

while connection.isconnected():
    params = {'bussen': 3}  
    response = requests.get(url, params=params)

    if response.status_code == 200:
        response_data = response.json() 
        print('Server response:', response_data)
    else:
        print('Error:', response.status_code)
