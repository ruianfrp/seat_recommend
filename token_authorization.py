from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def create_token(user_id):
    s = Serializer("classroom", expires_in=3600)
    # 接收用户id转换与编码
    authorization = s.dumps({"id": user_id}).decode("ascii")
    return authorization


def verify_token(authorization):
    s = Serializer("classroom")
    try:
        # 转换为字典
        data = s.loads(authorization)
    except Exception:
        return None
        # 拿到转换后的数据，根据模型类去数据库查询用户信息
    return data["id"]


if __name__ == '__main__':
    token = create_token("aaaaaaaaaaa")   #调用token对象
    print(token)
    print(verify_token(token))
