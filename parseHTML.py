import re

from bs4 import BeautifulSoup


def parseHtml(html):
    soup = BeautifulSoup(html, 'lxml')

    isEmpty_dic = {}
    classroom_roomInfo = []
    index = 0

    for i in soup.select('td[width="180"]'):
        s = re.findall('\S+', i.text)  # 正则表达式去除空行和换行
        classroom_roomInfo.append(s)

    for i in soup.find_all('tr',
                           onmouseover="var vpn_return;eval(vpn_rewrite_js((function () { this.style.cursor='hand' }).toString().slice(14, -2), 2));return vpn_return;"):
        # print(i.contents)
        classroom_timeInfo = i.contents[3::2]
        # print(classroom_timeInfo)
        isEmpty_boolList = []
        for j in classroom_timeInfo:
            str_temp = str(j)
            if len(str_temp) > 47:
                isEmpty_boolList.append(0)  # 被占用教室
            else:
                isEmpty_boolList.append(1)  # 空教室

        # print(isEmpty_boolList)
        isEmpty_dic[classroom_roomInfo[index][0]] = isEmpty_boolList
        index += 1

    return isEmpty_dic


if __name__ == '__main__':
    with open('res.html', 'r', encoding='utf-8') as f:
        h = f.read()
    print(str(parseHtml(h)))
