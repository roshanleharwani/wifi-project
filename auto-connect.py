import sys
import requests
import time
import pywifi
from pywifi import const
import colorama
import json
import subprocess
import platform
import os
import keyboard
from bs4 import BeautifulSoup
import threading

should_exit = False

threading.Thread(target=requests.packages.urllib3.disable_warnings).start()


def save_credentials(ssid, id, password):
    with open("cred.json", "w") as file:
        credentials = {"ssid": ssid, "id": id, "pass": password}
        json.dump(credentials, file)
        print(colorama.Fore.GREEN + "INFO - Credentials Saved!!")


def credentialsPresent():
    path = os.path.join(os.getcwd(), "cred.json")
    return os.path.exists(path)


def prompt(save_credentials):
    ssid = input("Enter Your Hostel Wi-Fi name: ")
    id = input("Enter your Registration Number: ")
    password = input("Enter your Wi-Fi password: ")
    save_credentials(ssid, id, password)
    print(colorama.Fore.GREEN + "Registered Successfully\n ")


def register(save_credentials):
    print(colorama.Fore.YELLOW + "Register for AutoConnect:")
    print(colorama.Fore.YELLOW + "[*] One Time Credential Submission\n")
    prompt(save_credentials)


if not credentialsPresent():
    register(save_credentials)


def read_credentials():
    try:
        with open("cred.json", "r") as file:
            credentials = json.load(file)
            return credentials
    except FileNotFoundError:
        print(colorama.Fore.RED + "ERROR - Credentials Not Found !!")
        print(colorama.Fore.YELLOW + "[*] One Time Credential Submission\n")
        ssid = input("Enter your Hostel Wi-Fi name: ")
        id = input("Enter your Registration Number: ")
        password = input("Enter your Wi-Fi password: ")
        save_credentials(ssid, id, password)
        return read_credentials()


try:
    ssid = read_credentials()["ssid"]
except:
    register(save_credentials)


def connect_to_open_wifi(ssid):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    iface.scan()
    time.sleep(1.5)
    scan_results = iface.scan_results()

    for result in scan_results:
        if result.ssid == ssid:
            profile_info = pywifi.Profile()
            profile_info.ssid = ssid
            profile_info.auth = const.AUTH_ALG_OPEN
            iface.remove_all_network_profiles()
            profile = iface.add_network_profile(profile_info)

            iface.connect(profile)
            time.sleep(3)

            if iface.status() == const.IFACE_CONNECTED:
                print(colorama.Fore.YELLOW + f"INFO - Connected to {ssid}")
            else:
                print(colorama.Fore.RED + f"ERROR - Failed to connect to {ssid}")

            break


def is_connected():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    if iface.status() in [pywifi.const.IFACE_DISCONNECTED, pywifi.const.IFACE_INACTIVE]:
        return False
    if iface.status() in [pywifi.const.IFACE_SCANNING, pywifi.const.IFACE_CONNECTING]:
        if iface.status() != pywifi.const.IFACE_CONNECTED:
            return False
    return True


def check_internet():
    try:
        subprocess.run(
            ["ping", "-n", "2", "google.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def connect(read_credentials, connect_to_open_wifi):
    while True:
        if check_internet():
            time.sleep(1)
        else:
            credentials = read_credentials()
            print(
                colorama.Fore.YELLOW
                + "INFO - Not Connected -Initiating internet connection..."
            )
            print(
                colorama.Fore.YELLOW + "[*] If Browser window pop up close that tab [*]"
            )
            if is_connected():
                break
            else:
                connect_to_open_wifi(credentials["ssid"])
                break

    url = "https://hfw.vitap.ac.in:8090/httpclient.html"

    credentials = read_credentials()

    form_data = {
        "mode": 191,
        "username": credentials["id"],
        "password": credentials["pass"],
    }

    response = requests.post(
        url,
        data=form_data,
        verify=False,
    )

    content = response.text
    soup = BeautifulSoup(content, "xml")

    message = soup.find("message").text.strip()

    if message == "You are signed in as {username}":
        print(colorama.Fore.GREEN + "INFO - Online")
        print(colorama.Fore.RED + "INFO - Press F7 to Sign out.")
    elif (
        message
        == "Login failed. Invalid user name/password. Please contact the administrator."
    ):
        print(colorama.Fore.RED + "Credentials are not valid !")
        prompt(save_credentials)
    else:
        print(colorama.Fore.RED + f"\n{message}\n")
        time.sleep(2.5)
        quit()


def disconnect():
    global should_exit
    url = "https://hfw.vitap.ac.in:8090/httpclient.html"
    credentials = read_credentials()
    form_data = {
        "mode": 193,
        "username": credentials["id"],
        "password": credentials["pass"],
    }
    requests.post(url, data=form_data, verify=False)
    print(colorama.Fore.RED + "WARNING - SIGNING OUT")
    should_exit = True


def internet():
    try:
        null_device = "/dev/null" if platform.system().lower() != "windows" else "NUL"
        subprocess.run(
            ["ping", "-n", "2", "google.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        # If an exception is raised, it means there is no internet connection
        connect(read_credentials, connect_to_open_wifi)


if check_internet():
    print(colorama.Fore.GREEN + "INFO - Online")
    print(colorama.Fore.RED + "INFO - Press F7 to Sign out.")


def on_key_event(event):
    if event.name == "f7":
        disconnect()


# Register the callback function
threading.Thread(target=keyboard.on_press, args=[on_key_event]).start()

while not should_exit:
    try:
        internet()
        time.sleep(2)
    except:
        print(colorama.Fore.YELLOW + "INFO - Waiting to Resolve DNS")
        connect_to_open_wifi(ssid)
sys.exit()
