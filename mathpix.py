import sys
import base64
import requests
import json


def recognize(number_of_operation, mathOperations):
    for index in range(number_of_operation):
        file_path = "croppedImage/cropped" + str(index) + ".jpg"
        image_uri = "data:image/jpg;base64," + (base64.b64encode(open(file_path, "rb").read())).decode('utf-8')
        r = requests.post("https://api.mathpix.com/v3/latex",
            data=json.dumps({'src': image_uri}),
            headers={"app_id": "mathpix", "app_key": "139ee4b61be2e4abcfb1238d9eb99902",
                    "Content-type": "application/json"})
        res = json.loads(r.text)
        mathOperations[index].operation = res['latex_list']
    return mathOperations
