def getBrandModel():
    with open('D:/ytx/space/python/3.6/scrapy_learn1v3/scrapy_learn1v3/utils/brandversion_temp.csv', 'r') as f:
        for item in f.readlines():
            temp = item.split(",")
            if len(temp) > 1:
                yield temp[0].strip(), temp[1].strip()

    pass


def saveBrandIgnore(brand, model):
    with open('D:/ytx/space/python/3.6/scrapy_learn1v3/scrapy_learn1v3/utils/brandversion_ignore.csv', 'a') as f:
        f.write(brand + "," + model)


def saveUrlIgnore(url, asin, comment_num):
    with open('D:/ytx/space/python/3.6/scrapy_learn1v3/scrapy_learn1v3/utils/amazon_ignoreUlr.txt', 'a') as f:
        f.write(url + "," + asin + "," + str(comment_num) + "\n")
    pass


def getUrlIgnore():
    with open('D:/ytx/space/python/3.6/scrapy_learn1v3/scrapy_learn1v3/utils/amazon_ignoreUlr.txt', 'r+') as f:
        for item in f:
            yield item.split(",")[0], item.split(",")[1]
        pass


if __name__ == '__main__':
    for item, model in getBrandModel():
        print(item)
