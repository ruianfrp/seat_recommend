from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

key = 'classroom'


# 加密内容需要长达16位字符，所以进行空格拼接
def pad(text):
    while len(text) % 16 != 0:
        text += ' '
    return text


# 加密秘钥需要长达16位字符，所以进行空格拼接
def pad_key(key):
    while len(key) % 16 != 0:
        key += ' '
    return key


# des加密
def encryption(text):
    # 进行加密算法，模式ECB模式，把叠加完16位的秘钥传进来
    aes = AES.new(pad_key(key).encode(), AES.MODE_ECB)
    # 进行内容拼接16位字符后传入加密类中，结果为字节类型
    encrypted_text = aes.encrypt(pad(text).encode())
    encrypted_text_hex = b2a_hex(encrypted_text)
    return encrypted_text_hex


# des解密
def decrypt(encrypted_text):
    aes = AES.new(pad_key(key).encode(), AES.MODE_ECB)
    de = str(aes.decrypt(a2b_hex(encrypted_text)), encoding='utf-8', errors="ignore")
    # #获取str从0开始到文本内容的字符串长度。
    return de.rstrip(' ')


if __name__ == '__main__':
    a = encryption('hello')
    print(str(a, 'utf-8'))
    b = decrypt(a)
    print(b)
