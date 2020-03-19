import pymysql
import AesCipher
import pandas as pd


# 登录校验
def mysql_login():
    try:
        db = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                             charset="utf8")
        cursor = db.cursor()  # 数据游标
        ret = cursor.execute("select * from classroom;")
        print("密码正确")
        print("{} rows in set.".format(ret))
        db.close()  # 关闭数据库
    except:
        print("密码错误")


# user录入
def user_insert(user_no, password):
    global cipher
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "insert into user(user_no,password) select %s,%s from dual where not EXISTS " \
          "(select user_no from user where user_no=%s);"
    if password != 'null':
        cipher = AesCipher.encryption(password)
        # print(cipher)
    try:
        # 执行SQL语句
        cursor.execute(sql, [user_no, cipher, user_no])
        # 提交事务
        conn.commit()
        # 提交之后，获取刚插入的数据的ID
        last_id = cursor.lastrowid
        if last_id != 0:
            print(last_id)
        else:
            print("用户已存在!")
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        print(e)
    cursor.close()
    conn.close()


def user_select(user_no):
    global ret
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 查询数据的SQL语句
    sql = "SELECT password from user WHERE user_no=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, user_no)
        ret = cursor.fetchone()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
        print(e)
    cursor.close()
    conn.close()
    return ret[0]


# 添加教室信息（单条）获得添加数据id
def classroom_insert(classroom_name):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "INSERT INTO classroom(classroom_name) VALUES (%s);"
    try:
        # 执行SQL语句
        cursor.execute(sql, [classroom_name])
        # 提交事务
        conn.commit()
        # 提交之后，获取刚插入的数据的ID
        last_id = cursor.lastrowid
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


# 添加教室信息（批量）
def classroom_insert_many(data):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "INSERT INTO classroom(classroom_name) VALUES (%s);"
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


# 删除classroom信息
def classroom_delete(classroom_id):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    sql = "DELETE FROM classroom WHERE id=%s;"
    try:
        cursor.execute(sql, [classroom_id])
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


# 修改教室信息
def classroom_update(classroom_name, classroom_id):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 修改数据的SQL语句
    sql = "UPDATE classroom SET classroom_name=%s WHERE id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, [classroom_name, classroom_id])
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


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
def seat_update(seat_state, seat_id):
    conn = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                           charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 修改数据的SQL语句
    sql = "UPDATE seat SET seat_state=%s WHERE id=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, [seat_state, seat_id])
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    user_insert('admin', 'Ab123456')
    a = user_select('admin')
    print(a)
    print(AesCipher.decrypt(a))
