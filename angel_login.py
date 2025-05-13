from dotenv import load_dotenv
import os
import pyotp
from SmartApi import SmartConnect

load_dotenv()


def get_smartconnect():
    api_key = os.getenv("API_KEY")
    client_id = os.getenv("USERNAME")
    mpin = os.getenv("MPIN")
    totp_token = os.getenv("TOTP_TOKEN")

    if not all([api_key, client_id, mpin, totp_token]):
        raise Exception("API_KEY, USERNAME, MPIN or TOTP_TOKEN missing in .env")

    sc = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_token)
    data = sc.generateSession(client_id, mpin, totp.now())

    auth_token = data["data"]["jwtToken"]
    feed_token = sc.getfeedToken()
    return sc, auth_token, feed_token
