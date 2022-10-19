import json
import re
import requests


def get_data_html():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 '
                      'Safari/535.1'}
    response = requests.get('https://ncov.dxy.cn/ncovh5/view/pneumonia?from=timeline&isappinstalled=0', headers=headers,
                            timeout=3)
    # 请求页面
    response = str(response.content, 'utf-8')
    # 中文重新编码
    return response
    # 返回了HTML数据


def get_data_dictype():
    areas_type_dic_raw = re.findall('try { window.getAreaStat = (.*?)}catch\(e\)', get_data_html())
    areas_type_dic = json.loads(areas_type_dic_raw[0])
    return areas_type_dic
    # 返回经过json转换过的字典化的数据


def paqu():  # 爬取数据并保存在Excel中
    for province_data in get_data_dictype():
        for citiy_data in province_data['cities']:
            # 该部分获取某个省下某城市的数据
            cityname = citiy_data['cityName']
            if cityname == "呼和浩特":
                c_currentconfirmedCount = citiy_data['currentConfirmedCount']
                c_confirmedcount = citiy_data['confirmedCount']
                c_suspectedcount = citiy_data['suspectedCount']
                c_curedcount = citiy_data['curedCount']
                c_deadcount = citiy_data['deadCount']
                c_locationid = citiy_data['locationId']
                dic2 = {
                    "城市": cityname,
                    "现存确诊": c_currentconfirmedCount,
                    "累计确诊": c_confirmedcount,
                    "疑似": c_suspectedcount,
                    "治愈": c_curedcount,
                    "死亡": c_deadcount,
                    "id": c_locationid
                }
    return dic2
