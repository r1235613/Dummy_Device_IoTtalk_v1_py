import time, random, requests
import DAN
import requests

ServerURL = 'http://192.168.113.105:9999'  # with non-secure connection
WEBTHING_URL = "http://192.168.113.106:8080"
Reg_addr = "MyLigut"  # 設備的唯一ＩＤ

DAN.profile['dm_name'] = 'wt-light'
DAN.profile['df_list'] = [
    "wt-switch-I",
    "wt-switch-O",
    "wt-colorTemperature-I",
    "wt-colorTemperature-O",
    "wt-Brightness-I",
    "wt-Brightness-O",
]
DAN.profile['d_name'] = 'MY_Light'  # 自己取名字吧


login_jwt = requests.post(WEBTHING_URL + "/login", headers={
    "Accept": "application/json",
}, data={
    "email": input("Please enter email of WebThings Gateway"),
    "password": input("Please enter password of WebThings Gateway")
}).json()['jwt']


def get_property(url, jwt, things, p):
    """

    :param url: WebThings實例的URL
    :param jwt: 認證用的口令
    :param things: 裝置ID
    :param p: 要讀取的成員
    :return:
    """
    r = requests.get(url + f"/things/{things}/properties/{p}", headers={
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    return r.json()[p]


def set_property(url, jwt, things, p, v):
    """

    :param url: WebThings實例的URL
    :param jwt: 認證用的口令
    :param things: 裝置ID
    :param p: 要設置的屬性名稱
    :param v: 要設置的值
    :return:
    """
    r = requests.put(url + f"/things/{things}/properties/{p}", headers={
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }, data={p: v})


DAN.device_registration_with_retry(ServerURL, Reg_addr)
# DAN.deregister()  #if you want to deregister this device, uncomment this line
# exit()            #if you want to deregister this device, uncomment this line

while True:
    try:
        DAN.push('wt-switch-I', get_property(WEBTHING_URL, login_jwt, "philips-hue-ecb5fafffe33c53e-1", "on"))  # Push data to an input device feature "Dummy_Sensor"
        DAN.push('wt-colorTemperature-I', get_property(WEBTHING_URL,login_jwt, "philips-hue-ecb5fafffe33c53e-1", "colorTemperature"))  # Push data to an input device feature "Dummy_Sensor"
        DAN.push('wt-Brightness-I', get_property(WEBTHING_URL,login_jwt, "philips-hue-ecb5fafffe33c53e-1", "level"))  # Push data to an input device feature "Dummy_Sensor"
        print(f'Data Send;on {get_property(WEBTHING_URL, login_jwt, "philips-hue-ecb5fafffe33c53e-1", "on")}; ct{get_property(WEBTHING_URL,login_jwt, "philips-hue-ecb5fafffe33c53e-1", "colorTemperature")}; level: {get_property(WEBTHING_URL,login_jwt, "philips-hue-ecb5fafffe33c53e-1", "level")}')
        # ==================================

        set_property(WEBTHING_URL, login_jwt, "philips-hue-ecb5fafffe33c53e-1", "on", 1 if DAN.pull('wt-switch-O') else 0)
        set_property(WEBTHING_URL, login_jwt, "philips-hue-ecb5fafffe33c53e-1", "colorTemperature", int(DAN.pull('wt-colorTemperature-O')))
        set_property(WEBTHING_URL, login_jwt, "philips-hue-ecb5fafffe33c53e-1", "level", 1 if DAN.pull('wt-Brightness-O') else 0)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)

    time.sleep(1)
