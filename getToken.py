import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import requests

url = "https://intg-engineer-server-929282497502.europe-west1.run.app/auth"

response = requests.post(url, json=body, )

if response.status_code == 200:
    data = response.json()
    auth_token = data.get("AccessToken")
    print("Successful! Token is: ", auth_token)
elif response.status_code == 400:
    print("Error 400: Bad request in case of invalid payload (missing or empty ProjectKey)")
elif response.status_code == 429:
    print("Error 429: Too many Requests if the API is under heavy load")
elif response.status_code == 500:
    print("Error 500: Internal server error if there is an error on the server side. The API is not always reliable.")
else:
    print("Failed", response.status_code, response.text)
