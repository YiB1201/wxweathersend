import os
import random
import sys
from datetime import datetime, date
from time import localtime
from requests import get, post
from zhdate import ZhDate
from yiqin import *

def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    return weather, temp, wind_dir


def get_festival(festival, year, today):
    festival_year = festival.split("-")[0]
    # 判断是否为农历生日
    if festival_year[0] == "r":
        r_mouth = int(festival.split("-")[1])
        r_day = int(festival.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            festival = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        festival_month = festival.month
        festival_day = festival.day
        # 今年生日
        year_date = date(year, festival_month, festival_day)

    else:
        # 获取国历生日的今年对应月和日
        festival_month = int(festival.split("-")[1])
        festival_day = int(festival.split("-")[2])
        # 今年生日
        year_date = date(year, festival_month, festival_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if festival_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), festival_month, festival_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


def send_message(to_user, access_token, region_name, weather, temp, wind_dir, xiancun, yisi, leiji, zhiyu, siwang,
                 note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取所有生日数据
    festival = {}
    for k, v in config.items():
        if k[0:5] == "festi":
            festival[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "region": {
                "value": region_name,
                "color": get_color()
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "temp": {
                "value": temp,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "xiancun": {
                "value": xiancun,
                "color": get_color()
            },
            "yisi": {
                "value": yisi,
                "color": get_color()
            },
            "leiji": {
                "value": leiji,
                "color": get_color()
            },
            "zhiyu": {
                "value": zhiyu,
                "color": get_color()
            },
            "siwang": {
                "value": siwang,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            }
        }
    }
    for key, value in festival.items():
        # 获取距离下次生日的时间
        festival_day = get_festival(value["data"], year, today)
        if festival_day == 0:
            festival_data = "今天{}哦，祝你{}快乐！".format(value["name"], value["name"])
        else:
            festival_data = "距离{}还有{}天".format(value["name"], str(int(festival_day)-1))
        # 将生日数据插入data
        data["data"][key] = {"value": festival_data, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp, wind_dir = get_weather(region)
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    if note_ch == "" and note_en == "":
        # 获取词霸每日金句
        note_ch, note_en = get_ciba()
    # 公众号推送消息
    dic = paqu()
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, dic["现存确诊"], dic["疑似"], dic["累计确诊"], dic["治愈"],
                     dic["死亡"], note_ch, note_en)
    os.system("pause")
