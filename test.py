import asyncio
import aiohttp
import platform
import subprocess
import time
import json
import pywifi
from pywifi import const
import colorama
import requests
from urllib3.exceptions import InsecureRequestWarning

colorama.init()
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

async def save_credentials(id,password):
    with open('cred.json','w') as file:
        credentials = {'id':id,'pass':password}
        json.dump(credentials,file)
        print(colorama.Fore.GREEN+'INFO - Credentials Saved!!')

async def read_credentials():
    try:
        with open('cred.json','r') as file:
            credentials  = json.load(file)
            return credentials
    except FileNotFoundError:
        print(colorama.Fore.RED+'ERROR - Credentials Not Found !!')
        print(colorama.Fore.YELLOW+'[*] One Time Credential Submission\n')
        id = input('Enter your Registration Number: ')
        password = input('Enter your Wi-Fi password: ')
        await save_credentials(id,password)
        return await read_credentials()

async def connect_to_open_wifi(ssid):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    iface.scan()
    await asyncio.sleep(2)
    scan_results = iface.scan_results()

    for result in scan_results:
        if result.ssid == ssid:
            profile_info = pywifi.Profile()
            profile_info.ssid = ssid
            profile_info.auth = const.AUTH_ALG_OPEN 
            iface.remove_all_network_profiles()
            profile = iface.add_network_profile(profile_info)

            iface.connect(profile)
            await asyncio.sleep(5)

            if iface.status() == const.IFACE_CONNECTED:
                print(colorama.Fore.YELLOW+f"INFO - Connected to {ssid}")
            else:
                print(colorama.Fore.RED+f"ERROR - Failed to connect to {ssid}")

            break

async def check_internet():
    try:
        null_device = '/dev/null' if platform.system().lower() != 'windows' else 'NUL'
        subprocess.run(['ping', '-n', '2', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

async def connect():
    if await check_internet():
        print(colorama.Fore.GREEN + 'INFO - Online')
        return

    print(colorama.Fore.YELLOW + 'INFO - Not Connected -Initiating internet connection...')
    await connect_to_open_wifi('VITAP-HOSTEL')

    url = 'https://hfw.vitap.ac.in:8090/httpclient.html'

    credentials = await read_credentials()

    form_data = {
        'mode':191,
        'username': credentials['id'],
        'password': credentials['pass'],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data, verify_ssl=False) as response:
            if response.status == 200:
                print(colorama.Fore.GREEN+'INFO - Online')
            else:
                print(colorama.Fore.RED+f'ERROR - while submitting form. Status code: {response.status}')
                print(await response.text())

async def internet():
    try:
        null_device = '/dev/null' if platform.system().lower() != 'windows' else 'NUL'
        subprocess.run(['ping', '-n', '2', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        # If an exception is raised, it means there is no internet connection
        await connect()

async def main():
    while True:
        try:
            await internet()
            await asyncio.sleep(4)
        except Exception as e:
            print(colorama.Fore.YELLOW+'INFO - Waiting to Resolve DNS')
            await connect_to_open_wifi('VITAP-HOSTEL')
            await asyncio.sleep(5)

asyncio.run(main())
