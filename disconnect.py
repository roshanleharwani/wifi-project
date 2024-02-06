import requests

def disconnect():
    url = 'https://hfw.vitap.ac.in:8090/httpclient.html'
    form_data = {
                'mode': 193,
                'username':'23bce7308',
                'password': 'GMZkY5ry',
            }
    requests.post(url,data=form_data,verify=False)


disconnect()