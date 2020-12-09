import time

from selenium.common.exceptions import NoSuchElementException

from parseHTML import parseHtml
import requests
import json
from selenium import webdriver


def postMsgHeader():
    """
    返回Post请求的头部，字典格式

    :return:字典格式的头部
    """

    global webVPNid

    """
        'Host': 'jwgl.bupt.edu.cn',
        'Origin': 'https://jwgl.bupt.edu.cn',
    """
    head_dic = {
        'Host': 'webvpn.bupt.edu.cn',
        'Origin': 'http://webvpn.bupt.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
        'Referer': 'http://webvpn.bupt.edu.cn/https/' + webVPNid + '/jsxsd/kbxx/jsjy_query'
    }
    return head_dic


def postMsgData(isHeadquarter=True):
    """
    返回Post请求的数据字段，字典格式

    :param isHeadquarter:是否查询本部？默认为是，否则查询沙河校区
    :return:字典格式的数据字段
    """

    # 需要根据学期查询（疑惑行为，不愧是傻逼教务）
    if int(time.localtime(time.time()).tm_mon) >= 8 or int(time.localtime(time.time()).tm_mon) <= 2:
        time_cur = str(time.localtime(time.time()).tm_year) + '-' + str(
            int(time.localtime(time.time()).tm_year) + 1) + '-1'
    else:
        time_cur = str(time.localtime(time.time()).tm_year - 1) + '-' + str(
            int(time.localtime(time.time()).tm_year)) + '-2'

    if isHeadquarter:
        campus_code = '01'  # 本部
    else:
        campus_code = '04'  # 沙河
    data_dic = {
        'typewhere': 'jszq',
        'xnxqh': time_cur,
        'gnq_mh': '',
        'jsmc_mh': '',
        'syjs0601id': '',
        'xqbh': campus_code,
        'jslx': '',
        'jxlbh': '',
        'jsbh': '',
        'bjfh': '=',
        'rnrs': '',
        'jszt': '5',
        'zc': '',
        'zc2': '',
        'xq': '',
        'xq2': '',
        'jc': '',
        'jc2': '',
        'kbjcmsid': '9475847A3F3033D1E05377B5030AA94D',
        'ssdw': ''
    }
    return data_dic


def getCookie():
    """
    利用selenium来获得cookie

    :return:字典格式的cookie
    """
    global webVPNid

    userAccount_xpath = '//*[@id="userAccount"]'
    passWord_xpath = '//*[@id="userPassword"]'
    login_xpath = '//*[@id="ul1"]/li[5]/button'

    vpnAccount_xpath = '//*[@id="user_name"]'
    vpnPassword_xpath = '/html/body/div[2]/div[2]/div[2]/div/form/div[4]/div/input'
    vpnLogin_xpath = '/html/body/div[2]/div[2]/div[2]/div/form/button'
    vpnContinue_xpath = '//*[@id="layui-layer1"]/div[3]/a[1]'

    vpnInput_xpath = '//*[@id="collapse-panel"]/div/div/div[1]/input'
    vpnJump_xpath = '//*[@id="go"]'

    # 静默运行，vpn环境下不可用
    # option = webdriver.ChromeOptions()
    # option.add_argument('headless')
    # 添加参数chrome_options=option

    driver = webdriver.Chrome()

    # https://jwgl.bupt.edu.cn/jsxsd/
    driver.get(
        'http://webvpn.bupt.edu.cn/')

    # 模拟输入/点击

    ## 登陆vpn
    driver.find_element_by_xpath(vpnAccount_xpath).send_keys(userAccount)
    driver.find_element_by_xpath(vpnPassword_xpath).send_keys(passWord)
    driver.find_element_by_xpath(vpnLogin_xpath).click()
    try:
        driver.find_element_by_xpath(vpnContinue_xpath).click()
    except NoSuchElementException:
        pass

    time.sleep(3)

    driver.find_element_by_xpath(vpnInput_xpath).send_keys('https://jwgl.bupt.edu.cn/jsxsd/')
    driver.find_element_by_xpath(vpnJump_xpath).click()

    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])

    driver.find_element_by_xpath(userAccount_xpath).send_keys(userAccount)
    driver.find_element_by_xpath(passWord_xpath).send_keys(passWord)
    driver.find_element_by_xpath(login_xpath).click()

    # print(driver.get_cookie('remember_token'))
    cookies_original = driver.get_cookies()
    print(driver.get_cookies())
    charIndex = 32
    for c in str(driver.current_url)[32:]:
        if c == '/':
            break
        charIndex += 1

    webVPNid = str(driver.current_url)[32:charIndex]

    # print(webVPNid)
    # eg. 'http://webvpn.bupt.edu.cn/https/77726476706e69737468656265737421fae0469069327d406a468ca88d1b203b/jsxsd/framework/xsMain.jsp'
    # print(cookies_original)

    cookies_dic = {
        cookies_original[0]['name']: cookies_original[0]['value'],
        cookies_original[1]['name']: cookies_original[1]['value']
    }

    return cookies_dic


def getJsonData(html_res: str):
    res_dic = parseHtml(html_res)
    day_dic = {1: 'MON', 2: 'TUE', 3: 'WED', 4: 'THU', 5: 'FRI', 6: 'SAT', 7: 'SUN'}
    result = {}

    for i, j in res_dic.items():
        week = 0
        index = 1
        if result.get(i, 0) == 0:
            result[i] = []
        for k in j:
            if index % 14 == 1:
                week += 1

            lesson_time = index % 14
            if lesson_time == 0:
                lesson_time = 14

            if k:
                # print('教室：' + i + day_dic[week] + ' 第' + str(lesson_time) + '节空闲！')
                result[i].append(str(week) + ' ' + str(lesson_time))
            index += 1

    return json.dumps(result)


# 全局变量，这里用我自己的学号密码登录的教务系统QAQ
userAccount = '你的学号'
passWord = '你登录教务网站的密码'
webVPNid = ''  # webVPN的url中附带的神秘代码


def getRoomInfo():
    """
    得到教室信息

    :param isHeadquarter: true为本部，false为沙河
    :return: json格式的信息
    """
    cookies = getCookie()

    session = requests.session()
    session.keep_alive = False

    # print(cookies)

    header = postMsgHeader()

    data_BenBu = postMsgData(True)
    data_ShaHe = postMsgData(False)

    r_BenBu = session.post(
        'http://webvpn.bupt.edu.cn/https/' + webVPNid + '/jsxsd/kbxx/jsjy_query2',
        data=data_BenBu, headers=header, cookies=cookies,
        verify=False)
    r_ShaHe = session.post(
        'http://webvpn.bupt.edu.cn/https/' + webVPNid + '/jsxsd/kbxx/jsjy_query2',
        data=data_ShaHe, headers=header, cookies=cookies,
        verify=False)

    # with open('res.html', 'w', encoding='utf-8') as f:
    #     f.write(res.text)

    json_BenBu = getJsonData(r_BenBu.text)
    json_ShaHe = getJsonData(r_ShaHe.text)
    dict_new = dict(json.loads(json_BenBu))
    dict_new.update(dict(json.loads(json_ShaHe)))
    json_all = json.dumps(dict_new)
    return [json_BenBu, json_ShaHe, json_all]


if __name__ == '__main__':
    getRoomInfo()
