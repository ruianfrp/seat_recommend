from flask import Flask, request, jsonify, abort
import json

import AesCipher
import mysql

app = Flask(__name__)
app.debug = True


# 登录
@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] != 'null' and request.form['password'] != 'null':
        username = request.form['username']
        password = request.form['password']
        cipher = AesCipher.decrypt(mysql.user_select(username))
        if password != cipher:
            error = '密码错误!'
            app.logger.error(error)
            return jsonify({"error": error}), 403
        else:
            info = "登陆成功!"
            app.logger.info(info)
            return jsonify({"info": info}), 200
    else:
        error = '请填写完整信息!'
        app.logger.error(error)
        return jsonify({"error": error}), 403


# 注册
@app.route('/register', methods=['POST'])
def register():
    if request.form['username'] != 'null' and request.form['password'] != 'null':
        username = request.form['username']
        password = request.form['password']
        return_id = mysql.user_insert(username, password)
        if return_id == 0:
            error = '已存在此用户'
            app.logger.error(error)
            return jsonify({"error": error}), 403
        elif return_id is str:
            error = return_id
            app.logger.error(error)
            return jsonify({"error": error}), 403
        else:
            info = '注册成功!'
            app.logger.info(info)
            return jsonify({"info": info}), 200


# 获取教室列表
@app.route('/classroom_show', methods=['GET'])
def get_classroom_info():
    result = mysql.classroom_select()
    if result is None:
        app.logger.error("数据库操作异常!")
        return jsonify({"error": "数据库操作异常!"}), 403
    elif result.__len__() == 0:
        app.logger.error("搜索数据为空!")
        return jsonify({"error": "搜索数据为空!"}), 403
    else:
        data = {}
        classrooms = []
        for r in result:
            classroom = {
                'id': r[0],
                'classroomName': r[1],
                'seatNum': r[2]
            }
            classrooms.append(classroom)
        data['classrooms'] = classrooms
        app.logger.info("教室信息返回成功!")
        return jsonify({"data": data, "info": "教室信息返回成功!"}), 200


# 获取实时教室座位信息
@app.route('/seat_real', methods=['POST'])
def get_real_seat_info():
    if request.form['classroom_id'] != 'null':
        classroom_id = request.form['classroom_id']
        result = mysql.seat_select(classroom_id)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"error": "数据库操作异常!"}), 403
        elif result.__len__() == 0:
            app.logger.error("搜索数据为空!")
            return jsonify({"error": "搜索数据为空!"}), 403
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
            return jsonify({"data": data, "info": "教室信息返回成功!"}), 200
    else:
        error = "返回教室id为空!"
        app.logger.error(error)
        return jsonify({"error": error}), 403


# 教室页面特殊位置搜索
@app.route('/classroom_special', methods=['POST'])
def get_special_classroom_info():
    if request.form['seat_place'] != 'null':
        seat_place = request.form['seat_place']
        result = mysql.classroom_special_select(seat_place)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"error": "数据库操作异常!"}), 403
        elif result.__len__() == 0:
            app.logger.info("所有教室已无此类型座位!")
            return jsonify({"info": "所有教室已无此类型座位!"}), 200
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
            return jsonify({"data": data, "info": "教室信息返回成功!"}), 200
    else:
        error = "特殊位置类型返回为空!"
        app.logger.error(error)
        return jsonify({"error": error}), 403


# 座位页面特殊位置搜索
@app.route('/seat_special', methods=['POST'])
def get_special_seat_info():
    if request.form['seat_place'] != 'null' and request.form['classroom_id'] != 'null':
        seat_place = request.form['seat_place']
        classroom_id = request.form['classroom_id']
        result = mysql.seat_special_select(seat_place, classroom_id)
        if result is None:
            app.logger.error("数据库操作异常!")
            return jsonify({"error": "数据库操作异常!"}), 403
        elif result.__len__() == 0:
            app.logger.info("此类型的位置已全部被占用!")
            return jsonify({"info": "此类型的位置已全部被占用!"}), 200
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
            return jsonify({"data": data, "info": "座位信息返回成功!"}), 200
    else:
        error = "返回为空!"
        app.logger.error(error)
        return jsonify({"error": error}), 403


if __name__ == '__main__':
    app.run()
