import sys
import base64
import requests
import json

file_path = 'test.jpg'
image_uri = "data:image/jpg;base64," + (base64.b64encode(open(file_path, "rb").read())).decode('utf-8')
r = requests.post("https://api.mathpix.com/v3/latex",
    data=json.dumps({'src': image_uri}),
    headers={"app_id": "mathpix", "app_key": "139ee4b61be2e4abcfb1238d9eb99902",
            "Content-type": "application/json"})
print(json.dumps(json.loads(r.text), indent=4, sort_keys=True))
