import os
import sys
import requests
import json
from dotenv import load_dotenv
import base64

OSH_URL = "https://api.getosh.com/osh"
API_KEY_FIELD = "OSH_API_KEY"
ENV_FILE = "~/.osh_env"
MAXLEN = 1800


def get_api_key_from_user():
    api_key = input("Please enter your OSH API key: ")
    if api_key_valid(api_key):
        with open(os.path.expanduser(ENV_FILE), 'w') as f:
            f.write(f"{API_KEY_FIELD}=" + api_key.strip())
    else:
        print("The API key you provided is invalid. "
              "You should have recevied the api key in the onboarding email from hello@getosh.com. ")
        sys.exit(1)


def api_key_valid(api_key):
    if api_key is not None and len(api_key.strip()) > 4:
        return True
    return False


def load_api_key_from_file():
    if os.path.isfile(os.path.expanduser(ENV_FILE)):
        load_dotenv(os.path.expanduser(ENV_FILE))
        key = os.getenv(API_KEY_FIELD)
        if api_key_valid(key):
            return key


def load_api_key():
    api_key = load_api_key_from_file()
    if not api_key_valid(api_key):
        get_api_key_from_user()
        api_key = load_api_key_from_file()
    if not api_key_valid(api_key):
        print("No API key provided. Exiting...")
        sys.exit(1)

    return api_key


def b64_encode(str_data):
    return base64.b64encode(str_data.encode('ascii'))


def call_model(input_data):
    body = {"commandDetails": b64_encode(json.dumps(input_data))}
    headers = {"apiKey": load_api_key()}
    return requests.get(OSH_URL, data=body, headers=headers).text


def call_llm_model(input_data):
    # take even number of args, where every pair represents key value
    data = {'command': input_data[0][:MAXLEN],
            'output': input_data[1][:MAXLEN],
            'returnStatus': input_data[2][:MAXLEN]}

    response = json.loads(call_model(data))
    if 'result' in response:
        print(response['result'])
    elif 'error' in response:
        print("An issue occurred while communicating with OSH servers: "+response['error'])



def main():
    args = sys.argv[1:]
    # args = ["rmdir aloha", "rmdir: aloha: Directory not empty", "1"]
    if len(args) == 3:
        load_api_key()
        call_llm_model(args)
    else:
        print("Invalid number of arguments provided: " + str(len(args)))


if __name__ == "__main__":
    main()
