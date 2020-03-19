from flask import Flask, request, jsonify, abort
import json

import AesCipher
import mysql

app = Flask(__name__)
app.debug = True


@app.route('/hello')
def hello_world():
    return 'Hello World!'


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


if __name__ == '__main__':
    app.run()
