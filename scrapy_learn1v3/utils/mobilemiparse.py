import json
import re


def test():
    with open("D:/ytx/space/python/3.6/scrapy_learn1v3/temp3.json", 'r') as f:
        data = f.readlines()
        data = "".join(data).replace("<br \/>\\n", "")
        data = "".join(data).replace("\\", "")
        data = re.sub("\s", " ", data)
        with open("D:/ytx/space/python/3.6/scrapy_learn1v3/temp4.json", 'w') as f2:
            f2.write(data)


def test2():
    with open("D:/ytx/space/python/3.6/scrapy_learn1v3/temp4.json", 'r') as f:
        data = json.load(f)
        print(data["data"])
        pass


def test3():
    with open("D:/ytx/space/python/3.6/scrapy_learn1v3/temp2.json", 'r') as f:
        data = json.load(f)
        print(data["data"])
        pass


if __name__ == '__main__':
    # test()
    # test2()
    test3()
