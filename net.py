# from flask import Flask, request, jsonify
# import json
#
# app = Flask(__name__)
# app.debug = True
#
#
# @app.route('/add/student/', methods=['post'])
# def add_stu():
#     if not request.data:  # 检测是否有数据
#         return 'fail'
#     student = request.data.decode('utf-8')
#     print(student)
#     # 获取到POST过来的数据，因为我这里传过来的数据需要转换一下编码。根据晶具体情况而定
#     student_json = json.loads(student)
#     # 把区获取到的数据转为JSON格式。
#     return jsonify(student_json)
#     # 返回JSON数据。
#
#
# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5438)
#     # 这里指定了地址和端口号。
import json

from flask import Flask, request, abort, Response
from flask_apscheduler import APScheduler

from selenium_brower import getRoomInfo

app = Flask(__name__)
scheduler = APScheduler()
data_ShaHe_json = ''
data_BenBu_json = ''
data_all_json = ''


class Config(object):
    JOBS = []


def crawlerTask():
    global data_ShaHe_json, data_BenBu_json, data_all_json
    data_BenBu_json, data_ShaHe_json, data_all_json = getRoomInfo()


@app.route('/', methods=['POST'])
def getPostData():
    """
    一个post请求应当包含多个个参数，包括：学号、密码、选择的校区、选择的时间（可以是多个）、选择的教学楼（可以是多个）

    :return:
    """

    dic = {}

    dataSet = request.get_data()
    dataSet = json.loads(dataSet)

    dic['id'] = dataSet.get('id', None)
    dic['password'] = dataSet.get('password', None)
    dic['campusCode'] = dataSet.get('campusCode', '0')  # 默认0为本部,1为沙河,2为全部
    dic['chosenTime'] = dataSet.get('chosenTime', '')
    dic['chosenBuilding'] = dataSet.get('chosenBuilding', '')
    dic['forceRefresh'] = dataSet.get('forceRefresh', 'false')

    if dic['id'] is None or dic['password'] is None:
        abort(403)

    if not(dic['id'] == '你设定的post ID' and dic['你设定的post 密码'] == 'lgh438'):
        abort(401)

    r = Response()
    # with open('start.html', 'r', encoding='utf-8') as f:
    #     r.data = f.read()
    r.headers['Content-Type'] = 'application/json;charset=utf-8'

    # 强制刷新
    if dic['forceRefresh'] == 'true':
        crawlerTask()

    if dic['campusCode'] == '1':
        # .encode('utf-8').decode('unicode-escape')
        r.data = data_ShaHe_json.encode('utf-8')
    elif dic['campusCode'] == '0':
        # .encode('utf-8').decode('unicode-escape')
        r.data = data_BenBu_json.encode('utf-8')
    else:
        r.data = data_all_json.encode('utf-8')

    return r  # 在此处将返回教室字典


# @app.route('/register', methods=['POST'])
# def register():
#     print(request.headers)
#     # print(request.stream.read())
#     print(request.form)
#     print(request.form['name'])
#     print(request.form.get('name'))
#     print(request.form.getlist('name'))
#     print(request.form.get('nickname', default='little apple'))
#     return 'welcome'


if __name__ == '__main__':
    crawlerTask()
    app.config.from_object(Config())
    scheduler.init_app(app=app)
    scheduler.start()
    scheduler.add_job(func=crawlerTask, id='1',
                      trigger='interval', seconds=1800, replace_existing=True)
    app.run(host='0.0.0.0', port=5438, debug=True, threaded=True)
