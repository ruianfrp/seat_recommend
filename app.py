import os

import keras
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from itsdangerous import Serializer
from concurrent.futures import ThreadPoolExecutor

import token_authorization

import AesCipher
import mysql
import functools

from yolo import YOLO

executor = ThreadPoolExecutor(10)
app = Flask(__name__)
CORS(app, supports_credentials=True)


# 座位获取（耗时任务）
def real_seat(classroom_id):
    keras.backend.clear_session()
    yolo = YOLO()
    try:
        image = Image.open("D:/SourceTree/yolov3/img/" + str(classroom_id) + ".jpg")
    except:
        app.logger.error("图片打开失败!")
    else:
        yolo.detect_image(image, classroom_id)
        app.logger.info("座位实时获取成功!")


# 在上面的基础上导入
def login_required(view_func):
    @functools.wraps(view_func)
    def verify_token(*args, **kwargs):
        try:
            # 在请求头上拿到token
            token = request.headers["Authorization"]
        except Exception:
            return jsonify(code=401, msg='缺少参数token')
        s = Serializer("classroom")
        try:
            s.loads(token)
        except Exception:
            return jsonify(code=401, msg="登录已过期")
        return view_func(*args, **kwargs)
    return verify_token


@app.route('/', methods=['GET'])
def ping_pong():
    return jsonify('Hello World!')


# 登录
@app.route('/login', methods=['POST'])
def login():
    if request.get_json().get('username') != 'null' and request.get_json().get('password') != 'null':
        username = request.get_json().get('username')
        pwd = request.get_json().get('password')
        result = mysql.user_select(username)
        password = str(AesCipher.encryption(pwd), 'utf-8')
        if password != result[2]:
            error = '密码错误!'
            app.logger.error(error)
            return jsonify({"code": 403, "error": error}), 403
        else:
            info = "登陆成功!"
            app.logger.info(info)
            tk = token_authorization.create_token(username)
            data = {}
            user = {
                'id': result[0],
                'userName': username,
                'userRole': result[3]
            }
            data['userInfo'] = user
            data['token'] = tk
            return jsonify({"code": 200, "data": data, "info": info}), 200
    else:
        error = '请填写完整信息!'
        app.logger.error(error)
        return jsonify({"code": 403, "error": error}), 403


# 注册
@app.route('/register', methods=['POST'])
def register():
    if request.get_json().get('username') != 'null' and request.get_json().get('password') != 'null':
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        return_id = mysql.user_insert(username, password)
        if return_id == 0:
            error = '已存在此用户'
            app.logger.error(error)
            return jsonify({"code": 403, "error": error}), 403
        elif return_id is str:
            error = return_id
            app.logger.error(error)
            return jsonify({"code": 403, "error": error}), 403
        else:
            info = '注册成功!'
            app.logger.info(info)
            return jsonify({"code": 200, "info": info}), 200


# 添加教室
@app.route('/classroom_insert', methods=['POST'])
def insert_classroom():
    if request.get_json().get('classroomName') is not None and \
            request.get_json().get('seatNums') is not None and \
            request.get_json().get('classroomInfo') is not None:
        classroom_name = request.get_json().get('classroomName')
        seat_nums = request.get_json().get('seatNums')
        classroom_info = request.get_json().get('classroomInfo')
        result = mysql.classroom_insert(classroom_name, seat_nums, classroom_info)
        if result is None:
            error = '数据库操作错误!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error})
        elif result == 0:
            error = '该教室已存在!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error})
        else:
            info = classroom_name + '教室添加成功!'
            app.logger.info(info)
            return jsonify({"code": 200, "info": info})
    else:
        error = '教室信息不得为空!'
        app.logger.info(error)
        return jsonify({"code": 403, "error": error})


# 删除教室
@app.route('/classroom_delete', methods=['POST'])
def delete_classroom():
    if request.get_json().get('id') != 'null':
        classroom_id = request.get_json().get('id')
        result = mysql.classroom_delete(classroom_id)
        if result == 'False':
            error = '数据库操作错误!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error})
        else:
            info = '教室删除成功!'
            app.logger.info(info)
            return jsonify({"code": 200, "info": info})
    else:
        error = '教室id返回为空!'
        app.logger.info(error)
        return jsonify({"code": 403, "error": error})

# 修改教室信息
@app.route('/classroom_update', methods=['POST'])
def update_classroom():
    if request.get_json().get('seatNums') is not None or request.get_json().get('classroomInfo') is not None:
        seat_num = request.get_json().get('seatNums')
        classroom_info = request.get_json().get('classroomInfo')
        classroom_id = request.get_json().get('id')
        result = mysql.classroom_update(seat_num, classroom_info, classroom_id)
        if result == 'False':
            error = '数据库操作错误!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error})
        else:
            info = '教室信息修改成功!'
            app.logger.info(info)
            return jsonify({"code": 200, "info": info})
    else:
        error = '返回参数不得全为空!'
        app.logger.info(error)
        return jsonify({"code": 403, "error": error})


# 获取教室列表
@app.route('/classroom_show', methods=['GET'])
def get_classroom_info():
    result = mysql.classroom_select()
    if result is None:
        app.logger.error("数据库操作异常!")
        return jsonify({"code": 403, "error": "数据库操作异常!"})
    elif result.__len__() == 0:
        app.logger.error("搜索数据为空!")
        return jsonify({"code": 403, "error": "搜索数据为空!"})
    else:
        data = {}
        classrooms = []
        for r in result:
            classroom = {
                'id': r[0],
                'classroomName': r[1],
                'seatNum': r[2],
                'freeSeatNum': r[3],
                'placeFreeSeat': 0,
                'classroomInfo': r[4]
            }
            classrooms.append(classroom)
        data['classrooms'] = classrooms
        app.logger.info("教室信息返回成功!")
        return jsonify({"code": 200, "data": data, "info": "教室信息返回成功!"})


# 获取座位数量
@app.route('/seat_num_get', methods=['get'])
def seat_num_get():
    result1, result2, result3, result4 = mysql.count_seat_select()
    if result1 is None or result2 is None or result3 is None or result4 is None:
        app.logger.error("数据库操作异常!")
        return jsonify({"code": 403, "error": "数据库操作异常!"})
    else:
        data = {}
        seatNums = []
        seatNum1 = {
            'seatPlaceNo': 0,
            'seatPlace': '普通',
            'counts': result1[0]
        }
        seatNums.append(seatNum1)
        seatNum2 = {
            'seatPlaceNo': 1,
            'seatPlace': '靠窗',
            'counts': result2[0]
        }
        seatNums.append(seatNum2)
        seatNum3 = {
            'seatPlaceNo': 2,
            'seatPlace': '靠门',
            'counts': result3[0]
        }
        seatNums.append(seatNum3)
        data['allSeatNum'] = result4[0]
        data['seatNums'] = seatNums
        app.logger.info("座位位置及数量返回成功!")
        return jsonify({"code": 200, "data": data, "info": "座位位置及数量返回成功!"})


# 获取实时教室座位信息
@app.route('/seat_real', methods=['POST'])
def get_real_seat_info():
    if request.get_json().get('classroomId') != 'null':
        classroom_id = request.get_json().get('classroomId')
        # 异步
        executor.submit(real_seat(classroom_id))

        result_max = mysql.seat_max_select(classroom_id)
        result = mysql.seat_real_select(classroom_id)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"})
        elif result.__len__() == 0:
            app.logger.error("搜索数据为空!")
            return jsonify({"code": 403, "error": "搜索数据为空!"})
        else:
            data = {}
            seats = [[2 for i in range(result_max[1])] for j in range(result_max[0])]
            for r in result:
                seats[r[1]-1][r[2]-1] = r[3]
            data['seats'] = seats
            app.logger.info("座位信息返回成功!")
            return jsonify({"code": 200, "data": data, "info": "座位信息返回成功!"})
    else:
        error = "返回教室id为空!"
        app.logger.error(error)
        return jsonify({"code": 403, "error": error})


# 教室页面特殊位置搜索
@app.route('/classroom_special', methods=['POST'])
def get_special_classroom_info():
    if request.get_json().get('seatPlace') != 'null':
        seatPlace = request.get_json().get('seatPlace')
        result = mysql.classroom_special_select(seatPlace)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"})
        else:
            data = {}
            classrooms = []
            for r in result:
                if r[4] != 0:
                    classroom = {
                        'id': r[0],
                        'classroomName': r[1],
                        'seatNum': r[2],
                        'freeSeatNum': r[3],
                        'placeFreeSeat': r[4],
                        'classroomInfo': r[5]
                    }
                    classrooms.append(classroom)
            if len(classrooms) == 0:
                app.logger.info("所有教室已无此类型座位!")
                return jsonify({"code": 400, "info": "所有教室已无此类型座位!"})
            data['classrooms'] = classrooms
            app.logger.info("位置推荐返回成功!")
            return jsonify({"code": 200, "data": data, "info": "位置推荐返回成功!"})
    else:
        error = "特殊位置类型返回为空!"
        app.logger.error(error)
        return jsonify({"code": 403, "error": error})


# 获取教室信息
@app.route('/get_classInfo_by_id', methods=['POST'])
def get_classInfo_by_id():
    if request.get_json().get('classroomId') != 'null':
        classroomId = request.get_json().get('classroomId')
        result = mysql.get_classInfo_by_id(classroomId)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"})
        else:
            data = {}
            classroom = {
                'id': result[0],
                'classroomName': result[1],
                'seatNum': result[2],
                'freeSeatNum': result[3],
                'classroomInfo': result[4]
            }
            data['classroom'] = classroom
            app.logger.info("教室信息返回成功!")
            return jsonify({"code": 200, "data": data, "info": "教室信息返回成功!"})
    else:
        error = "返回教室id为空!"
        app.logger.error(error)
        return jsonify({"code": 403, "error": error})


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
