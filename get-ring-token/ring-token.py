import json
import getpass
from pathlib import Path
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

my_email=input("PLease enter the email account for your Ring account: ")
cache_file = Path(my_email)


def token_updated(token):
    cache_file.write_text(json.dumps(token))


def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code


def main():
    if cache_file.is_file():
        print("Token has already been set up, loading...")
        auth = Auth("MyProject/1.0", json.loads(cache_file.read_text()), token_updated)
    else:
        username = my_email
        print("This is the first time setting up, getting the token set up now...")
        password = getpass.getpass("Password: ")
        auth = Auth("MyProject/1.0", None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, otp_callback())

    ring = Ring(auth)
    ring.update_data()


if __name__ == "__main__":
    main()
