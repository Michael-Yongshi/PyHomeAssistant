import os
import requests


def post_event_tester(event, json):

    # default address for home assistant to receive events
    url = f"http://rpi-home:8123/api/events/{event}"

    # open file with the api token
    token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')
    with open(token_filepath, "r") as text_file:
        token = text_file.read().strip("\n")

    # set up headers with token and content type json string
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    # send out the actual request to the api
    response = requests.post(url=url, headers=headers, json=json)

    print(response)

if __name__ == "__main__":

    post_event_tester(
        event="LIGHT_OVERRIDE", 
        json={
            "status": "on",
            },
        )