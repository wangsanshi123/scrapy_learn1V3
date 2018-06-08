# 使用python自带的hashlib库
import hashlib


def get_md5_value(str):
    my_md5 = hashlib.md5()  # 获取一个MD5的加密算法对象
    my_md5.update(str)  # 得到MD5消息摘要
    my_md5_Digest = my_md5.hexdigest()  # 以16进制返回消息摘要，32位
    return my_md5_Digest


if __name__ == '__main__':
    # print(get_md5_value("fljflajlfjaljflajflajf"))
    import hashlib

    md5 = hashlib.md5('yuan'.encode('utf - 8')).hexdigest()
    md6 = hashlib.md5('fajflajflajfljalfjajfljaflajlfjaljflajflajflajlfjaljflajflajfaljflajfjlajljfaljflajflajflajflajflajflajflajflajflajflajflajflajfljaljfqurq0uovjaugq-utr-ufg-aU'.encode('utf - 8')).hexdigest()

    print(md5)
    print(md6)