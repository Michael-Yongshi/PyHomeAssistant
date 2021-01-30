import requests

# default address for the rest api in default settings
url = "http://homeassistant:8123/api/"

# send the authorization token (long lived tokens in settings)
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkYWZjMWZhOTdiNzQ0N2MzYTdkMGM0NTZiOGI5MGY3NiIsImlhdCI6MTYxMjAxMTk3MiwiZXhwIjoxOTI3MzcxOTcyfQ.yKc0kqTgX5FCVbnP85pCw9bsWD-bKYkxBlXnUzNfxt8",
}

# send out the actual request to the api
response = requests.get(url=url, headers=headers)

print(response.text)