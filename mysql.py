import pymysql
from flask import json

import AesCipher
import pandas as pd


# 登录校验
def mysql_login():
    try:
        db = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                             charset="utf8")
        cursor = db.cursor()  # 数据游标
        cursor.execute("select version();")
        data = cursor.fetchone()
        print(data)
        # print("{} rows in set.".format(ret))
        db.close()  # 关闭数据库
    except:
        print("密码错误")


# user录入
def user_insert(username, password):
    global cipher
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "insert into user(user_no,password) select %s,%s from dual where not EXISTS " \
          "(select user_no from user where user_no=%s);"
    if password != 'null':
        cipher = str(AesCipher.encryption(password), 'utf-8')
        # print(cipher)
    try:
        # 执行SQL语句
        cursor.execute(sql, [username, cipher, username])
        # 提交事务
        conn.commit()
        # 提交之后，获取刚插入的数据的ID
        last_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return last_id
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return str(e)


# 搜索用户密码（登陆时）
def user_select(user_no):
    global ret
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT id, user_no, password, user_role from user WHERE user_no=%s;"
    try:
        # 执行SQL语句（防止注入）
        cursor.execute(sql, user_no)
        ret = cursor.fetchall()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()
    return ret[0]


# 添加教室信息（单条）获得添加数据id
def classroom_insert(classroom_name, seat_nums, classroom_info):
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "insert into classroom(classroom_name,seat_num,classroom_info) select %s,%s,%s from dual " \
          "where not EXISTS (select classroom_name from classroom where classroom_name=%s);"
    try:
        # 执行SQL语句
        cursor.execute(sql, [classroom_name, seat_nums, classroom_info, classroom_name])
        # 提交事务
        conn.commit()
        # 提交之后，获取刚插入的数据的ID
        result = cursor.lastrowid
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 根据id删除教室信息
def classroom_delete(classroom_id):
    result = 'False'
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "delete from classroom where id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, [classroom_id])
        # 提交事务
        conn.commit()
        # 提交之后，获取刚插入的数据的ID
        cursor.close()
        conn.close()
        result = 'True'
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 修改教室信息
def classroom_update(seat_num, classroom_info, classroom_id):
    result = 'False'
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 修改数据的SQL语句
    sql = "UPDATE classroom SET seat_num=%s, classroom_info=%s WHERE id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, [seat_num, classroom_info, classroom_id])
        # 提交事务
        conn.commit()
        cursor.close()
        conn.close()
        result = 'True'
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 添加座位信息（批量）
def seat_insert_many(data):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "INSERT INTO seat(fk_classroom_id, seat_real_x, seat_real_y, seat_pic_x, seat_pic_y, seat_state, " \
          "seat_place) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    # data = [("Alex", 18), ("Egon", 20), ("Yuan", 21)]
    try:
        # 批量执行多条插入SQL语句
        cursor.executemany(sql, data)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


# 修改座位信息
def seat_update(seat_id):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 修改数据的SQL语句
    sql = "UPDATE seat SET seat_state=1 WHERE id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, seat_id)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


# 教室信息查询
def classroom_select():
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT c.id, c.classroom_name, c.seat_num,(select count(s.id) from seat as s where " \
          "s.fk_classroom_id=c.id and seat_state=0) as free_seat_num,classroom_info FROM classroom as c;"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取多条查询数据
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 剩余位置总数获取
def count_free_seat():
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT count(id) FROM seat where seat_state=0;"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取多条查询数据
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 特殊座位总数获取
def count_seat_select():
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT seat_place,count(1) as counts FROM seat_recommend.seat where seat_state=0 group by seat_place;"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取多条查询数据
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 座位信息查询
def seat_real_select(classroom_id):
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT id, seat_state from seat where fk_classroom_id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, classroom_id)
        # 获取多条查询数据
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 特殊位置空余搜索（教室页面搜索）
def classroom_special_select(seat_place):
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT s.fk_classroom_id, c.seat_num, count(s.id) as seat_free from seat as s left join classroom as c " \
          "on c.id=s.fk_classroom_id where s.seat_place=%s and s.seat_state=0 group by s.fk_classroom_id"
    try:
        # 执行SQL语句
        cursor.execute(sql, seat_place)
        # 获取多条查询数据
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 特殊位置空余搜索（座位页面搜索）
def seat_special_select(seat_place, classroom_id):
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT id from seat where seat_state=0 and seat_place=%s and fk_classroom_id=%s"
    try:
        # 执行SQL语句
        cursor.execute(sql, [seat_place, classroom_id])
        # 获取多条查询数据
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


# 搜索人物是否在某个位置上(包含初始化座位信息)
def seat_select(pic_x, pic_y, classroom_id):
    result = None
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 座位初始化
    # 初始化座位信息SQL语句
    sql1 = "UPDATE seat SET seat_state=0 WHERE fk_classroom_id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql1, classroom_id)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()

    # 查询数据
    # 查询数据的SQL语句
    sql2 = "SELECT id, seat_pic_top, seat_pic_bottom, seat_pic_left, seat_pic_right FROM seat_recommend.seat where " \
           "seat_pic_left<%s and seat_pic_right>%s and seat_pic_top<%s and seat_pic_bottom>%s and fk_classroom_id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql2, [pic_x, pic_x, pic_y, pic_y, classroom_id])
        # 获取多条查询数据
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        cursor.close()
        conn.close()
        return result


if __name__ == "__main__":
    # user_insert("ccc", "Ab123456")
    # print(user_select("aaa") == str(AesCipher.encryption("Ab123456"), 'utf-8'))
    mysql_login()
