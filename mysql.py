import pymysql


# 登录校验
def mysql_login():
    try:
        db = pymysql.connect(host="localhost", user="root", password="123456", database="seat_recommend",
                             charset="utf8")
        cursor = db.cursor()  # 数据游标
        ret = cursor.execute("select * from classroom;")
        print("{} rows in set.".format(ret))
        db.close()  # 关闭数据库
        print("密码正确")
    except:
        print("密码错误")


if __name__ == "__main__":
    mysql_login()
