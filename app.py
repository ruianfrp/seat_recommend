from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import token_authorization
import json

import AesCipher
import mysql
from yolo import YOLO
from PIL import Image

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/', methods=['GET'])
def ping_pong():
    return jsonify('Hello World!')


# 登录
@app.route('/login', methods=['POST'])
def login():
    if request.get_json().get('username') != 'null' and request.get_json().get('password') != 'null':
        username = request.get_json().get('username')
        pwd = request.get_json().get('password')
        cipher = mysql.user_select(username)
        password = str(AesCipher.encryption(pwd), 'utf-8')
        if password != cipher:
            error = '密码错误!'
            app.logger.error(error)
            return jsonify({"code": 403, "error": error}), 403
        else:
            info = "登陆成功!"
            app.logger.info(info)
            tk = token_authorization.generate_token(username, 3600)
            return jsonify({"code": 200, "info": info, "token": tk}), 200
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
    if request.get_json().get('classroom_name') != 'null':
        classroom_name = request.get_json().get('classroom_name')
        result = mysql.classroom_insert(classroom_name)
        if result is None:
            error = '数据库操作错误!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error}), 403
        elif result == 0:
            error = '该教室已存在!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error}), 403
        else:
            info = '教室添加成功!'
            app.logger.info(info)
            return jsonify({"code": 200, "info": info}), 200
    else:
        error = '教室名称返回为空!'
        app.logger.info(error)
        return jsonify({"code": 403, "error": error}), 403


# 删除教室
@app.route('/classroom_delete', methods=['POST'])
def delete_classroom():
    if request.get_json().get('id') != 'null':
        classroom_id = request.get_json().get('id')
        result = mysql.classroom_delete(classroom_id)
        if result == 'False':
            error = '数据库操作错误!'
            app.logger.info(error)
            return jsonify({"code": 403, "error": error}), 403
        else:
            info = '教室添加成功!'
            app.logger.info(info)
            return jsonify({"code": 200, "info": info}), 200
    else:
        error = '教室id返回为空!'
        app.logger.info(error)
        return jsonify({"code": 403, "error": error}), 403


# 获取教室列表
@app.route('/classroom_show', methods=['GET'])
def get_classroom_info():
    result = mysql.classroom_select()
    if result is None:
        app.logger.error("数据库操作异常!")
        return jsonify({"code": 403, "error": "数据库操作异常!"}), 403
    elif result.__len__() == 0:
        app.logger.error("搜索数据为空!")
        return jsonify({"code": 403, "error": "搜索数据为空!"}), 403
    else:
        data = {}
        classrooms = []
        for r in result:
            classroom = {
                'id': r[0],
                'classroomName': r[1],
                'seatNum': r[2],
                'freeSeatNum': r[3],
                'classroomInfo': r[4]
            }
            classrooms.append(classroom)
        data['classrooms'] = classrooms
        app.logger.info("教室信息返回成功!")
        return jsonify({"code": 200, "data": data, "info": "教室信息返回成功!"}), 200


# 获取座位数量
@app.route('/seat_num_get', methods=['get'])
def seat_num_get():
    result1 = mysql.count_seat_select()
    if result1 is None:
        app.logger.error("数据库操作异常!")
        return jsonify({"code": 403, "error": "数据库操作异常!"}), 403
    elif result1.__len__() == 0:
        app.logger.error("搜索数据为空!")
        return jsonify({"code": 403, "error": "搜索数据为空!"}), 403
    else:
        result2 = mysql.count_free_seat()
        if result2 is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"}), 403
        elif result2[0] == 0:
            app.logger.error("搜索数据为空!")
            return jsonify({"code": 403, "error": "搜索数据为空!"}), 403
        else:
            data = {}
            seatNums = []
            for r in result1:
                if r[0] == 0:
                    seatNum = {
                        'seatPlace': '普通',
                        'counts': r[1]
                    }
                elif r[0] == 1:
                    seatNum = {
                        'seatPlace': '靠窗',
                        'counts': r[1]
                    }
                else:
                    seatNum = {
                        'seatPlace': '靠门',
                        'counts': r[1]
                    }
                seatNums.append(seatNum)
            data['allSeatNum'] = result2[0]
            data['seatNums'] = seatNums
            app.logger.info("座位位置及数量返回成功!")
            return jsonify({"code": 200, "data": data, "info": "座位位置及数量返回成功!"}), 200


# 获取实时教室座位信息
@app.route('/seat_real', methods=['POST'])
def get_real_seat_info():
    if request.get_json().get('classroom_id') != 'null':
        classroom_id = request.get_json().get('classroom_id')
        # 调用预测模型进行预测
        yolo = YOLO()
        try:
            image = Image.open("D:/SourceTree/yolov3/img/" + classroom_id + ".jpg")
        except:
            app.logger.error("图片打开失败!")
            return jsonify({"code": 403, "error": "图片打开失败!"}), 403
        else:
            yolo.detect_image(image, classroom_id)
        app.logger.info("教室" + classroom_id + "座位实时获取成功!")
        yolo.close_session()

        # 返回座位信息
        result = mysql.seat_select(classroom_id)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"}), 403
        elif result.__len__() == 0:
            app.logger.error("搜索数据为空!")
            return jsonify({"code": 403, "error": "搜索数据为空!"}), 403
        else:
            data = {}
            seats = []
            for r in result:
                seat = {
                    'id': r[0],
                    'seatState': r[1]
                }
                seats.append(seat)
            data['seats'] = seats
            app.logger.info("教室信息返回成功!")
            return jsonify({"code": 200, "data": data, "info": "教室信息返回成功!"}), 200
    else:
        error = "返回教室id为空!"
        app.logger.error(error)
        return jsonify({"code": 403, "error": error}), 403


# 教室页面特殊位置搜索
@app.route('/classroom_special', methods=['POST'])
def get_special_classroom_info():
    if request.form['seat_place'] != 'null':
        seat_place = request.form['seat_place']
        result = mysql.classroom_special_select(seat_place)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"}), 403
        elif result.__len__() == 0:
            app.logger.info("所有教室已无此类型座位!")
            return jsonify({"code": 200, "info": "所有教室已无此类型座位!"}), 200
        else:
            data = {}
            classrooms = []
            for r in result:
                classroom = {
                    'classroom_id': r[0],
                    'seat_num': r[1],
                    'seat_free': r[2]
                }
                classrooms.append(classroom)
            data['classrooms'] = classrooms
            app.logger.info("教室信息返回成功!")
            return jsonify({"code": 200, "data": data, "info": "教室信息返回成功!"}), 200
    else:
        error = "特殊位置类型返回为空!"
        app.logger.error(error)
        return jsonify({"code": 403, "error": error}), 403


# 座位页面特殊位置搜索
@app.route('/seat_special', methods=['POST'])
def get_special_seat_info():
    if request.form['seat_place'] != 'null' and request.form['classroom_id'] != 'null':
        seat_place = request.form['seat_place']
        classroom_id = request.form['classroom_id']
        result = mysql.seat_special_select(seat_place, classroom_id)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"code": 403, "error": "数据库操作异常!"}), 403
        elif result.__len__() == 0:
            app.logger.info("此类型的位置已全部被占用!")
            return jsonify({"code": 200, "info": "此类型的位置已全部被占用!"}), 200
        else:
            data = {}
            seats = []
            for r in result:
                seat = {
                    'id': r[0]
                }
                seats.append(seat)
            data['seats'] = seats
            app.logger.info("座位信息返回成功!")
            return jsonify({"code": 200, "data": data, "info": "座位信息返回成功!"}), 200
    else:
        error = "request返回为空!"
        app.logger.error(error)
        return jsonify({"code": 403, "error": error}), 403


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
