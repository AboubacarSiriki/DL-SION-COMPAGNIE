import os
import http.client
import json
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

API_KEY = os.getenv('INFOBIP_API_KEY')
API_URL = os.getenv('INFOBIP_API_URL')

def envoyer_sms_api(message, sender):
    conn = http.client.HTTPSConnection(API_URL)
    payload = json.dumps({
        "messages": [
            {
                "destinations": [{"to":"2250768140413"}, {"to":"2250759934211"}],
                "from": sender,
                "text": message
            }
        ]
    })
    headers = {
        'Authorization': f'App {API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")
