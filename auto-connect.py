import requests
import time
import pywifi
from pywifi import const
import colorama
import json
import subprocess
import platform
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

def save_credentials(id,password):
    with open('cred.json','w') as file:
        credentials = {'id':id,'pass':password}
        json.dump(credentials,file)
        print(colorama.Fore.GREEN+'INFO - Credentials Saved!!')

def read_credentials():
    try:
        with open('cred.json','r') as file:
            credentials  = json.load(file)
            return credentials
    except FileNotFoundError:
        print(colorama.Fore.RED+'ERROR - Credentials Not Found !!')
        print(colorama.Fore.YELLOW+'[*] One Time Credential Submission\n')
        id = input('Enter your Registration Number: ')
        password = input('Enter your Wi-Fi password: ')
        save_credentials(id,password)
        return read_credentials()

def connect_to_open_wifi(ssid):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    iface.scan()
    time.sleep(2)
    scan_results = iface.scan_results()

    for result in scan_results:
        if result.ssid == ssid:
            profile_info = pywifi.Profile()
            profile_info.ssid = ssid
            profile_info.auth = const.AUTH_ALG_OPEN 
            iface.remove_all_network_profiles()
            profile = iface.add_network_profile(profile_info)

            iface.connect(profile)
            time.sleep(5)

            if iface.status() == const.IFACE_CONNECTED:
                print(colorama.Fore.YELLOW+f"INFO - Connected to {ssid}")
            else:
                print(colorama.Fore.RED+f"ERROR - Failed to connect to {ssid}")

            break
    
def check_internet():
    try:
        null_device = '/dev/null' if platform.system().lower() != 'windows' else 'NUL'
        subprocess.run(['ping', '-n', '2', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    
def connect(read_credentials, connect_to_open_wifi):
    if check_internet():
        print(colorama.Fore.GREEN + 'INFO - Online')
    while True:
        if check_internet():
            time.sleep(5)  # Sleep for 5 seconds before checking again
        else:
            print(colorama.Fore.YELLOW + 'INFO - Not Connected -Initiating internet connection...')
            connect_to_open_wifi('VITAP-HOSTEL')
            break

    url = 'https://hfw.vitap.ac.in:8090/httpclient.html'

    credentials = read_credentials()

    form_data = {
    'mode':191,
    'username': credentials['id'],
    'password': credentials['pass'],
}

# Send a POST request to submit the form
    
    response = requests.post(url, data=form_data,verify=False,)

# Check the response
    if response.status_code == 200:
        print(colorama.Fore.GREEN+'INFO - Online')
    else:
        print(colorama.Fore.RED+f'ERROR - while submitting form. Status code: {response.status_code}')
        print(response.text)

def internet():
    try:
        null_device = '/dev/null' if platform.system().lower() != 'windows' else 'NUL'
        subprocess.run(['ping', '-n', '2', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        # If an exception is raised, it means there is no internet connection
        connect(read_credentials, connect_to_open_wifi)
if check_internet():
    print(colorama.Fore.GREEN+'INFO - Online')
while True:
    try:
        internet()
        time.sleep(4)
    except:
        print(colorama.Fore.YELLOW+'INFO - Waiting to Resolve DNS')
        connect_to_open_wifi('VITAP-HOSTEL')
        time.sleep(5)