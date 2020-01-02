import requests
import os

from dotenv import load_dotenv


def get_reviews(dvmn_toke):
    dvmn_url = "https://dvmn.org/api/user_reviews/"
    headers = {"Authorization": f"Token {dvmn_token}"}
    response = requests.get(dvmn_url, headers=headers)
    return response.text


if __name__ == "__main__":
    load_dotenv()
    dvmn_token = os.environ['token']
    print(dvmn_token)
    dvmn_resp = get_reviews(dvmn_token)
    print(dvmn_resp)
