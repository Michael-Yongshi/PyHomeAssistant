import requests

# default address for the rest api in default settings
url = "http://homeassistant:8123/api/events/API_EVENT"

# send the authorization token (long lived tokens in settings) and denote that we are sending data in the form of a json string
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkYWZjMWZhOTdiNzQ0N2MzYTdkMGM0NTZiOGI5MGY3NiIsImlhdCI6MTYxMjAxMTk3MiwiZXhwIjoxOTI3MzcxOTcyfQ.yKc0kqTgX5FCVbnP85pCw9bsWD-bKYkxBlXnUzNfxt8"
headers = {
    "Authorization": f"Bearer {token}",
    "content-type": "application/json",
}

# the data to be posted
data = {}
# data = {
#     "key": "value"
# }

# send out the actual request to the api
response = requests.post(url=url, headers=headers, data=data)

print(response.text)