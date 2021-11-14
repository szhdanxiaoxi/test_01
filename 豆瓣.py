# 引入需要的包
from bs4 import BeautifulSoup   # 网页解析
import re    # 正则表达式
import urllib.request,urllib.error   # 制定url，获取网页数据
import xlwt  # 进行Excel操作
import sqlite3   # 进行sqlite数据库操作    # #



def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 1.爬取网页
    datalist = getData(baseurl)
    #savepath = ".\\douban_moive.xls"
    dbpath = "movie.db"

    # 3.保存数据
    #saveData(datalist,savepath)
    saveData2DB(datalist,dbpath)

    # askURL("https://movie.douban.com/top250?start=")
# 全局变量
# 链接
findLink = re.compile(r'<a href="(.*?)">')         # 创建正则表达式，表示规则
# 图片
findImgSrc =  re.compile(r'<img.*src="(.*?)" ',re.S) # re.S让换行符包含在字符中
# 片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#  找到评价人数
findJuge = re.compile(r'<span>(\d*)人评价</span>')
# 概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)
#  爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0,10):       # 调用获取页面信息的函数，10次
        url = baseurl + str(i*25)
        html = askURL(url)  # 一页html，保存获取到的网页源码。

        # 2.逐一解析数据
        soup = BeautifulSoup(html, "html.parser")  # 用parser解析html
        # print(soup)
        for item in soup.find_all('div',class_="item"):   # 查找符合要求的字符串，形成列表
            # print(item)
            data = []  # 保存一部电影的全部信息
            item = str(item)

            # 影片详细链接
            link = re.findall(findLink,item)[0]  # re库通过正则表达式查找指定的字符串
            data.append(link)
            imgSrc = re.findall(findImgSrc,item)[0] # 添加图片
            data.append(imgSrc)
            titles = re.findall(findTitle,item)
            if(len(titles) == 2): # 添加标题，可能只有中文，可能中外都有
                ctitle = titles[0]
                data.append(ctitle)  # 添加中文名
                otitle = titles[1].replace("/","") # 去掉无关的符号
                otitle = re.sub('\s'," ",otitle)
                data.append(otitle)  # 添加外国名
            else:
                data.append(titles[0])
                data.append(' ')
            rating = re.findall(findRating,item)[0]
            data.append(rating)  # 添加评分
            jugeNum = re.findall(findJuge,item)[0]
            data.append(jugeNum)  # 添加评价人数

            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。","") # 去掉句号
                data.append(inq)
            else:
                data.append(" ")
            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd) # 去掉<br/>
            bd = re.sub('/'," ",bd) # 去掉/
            bd = re.sub(r'\s'," ",bd)
            data.append(bd.strip()) # 去掉前后空格


            datalist.append(data)
    # print(datalist)



    return datalist

# 得到某个指定url的网页内容（模拟浏览器访问）
def askURL(url):
    # 模拟浏览器头部信息
    head = {
        # 用户代理，告诉浏览器我们是什么机器，什么浏览器。（来自于浏览器）
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
            }
    request = urllib.request.Request(url,headers=head)  # 请求访问，放入头部信息
    html = ""  # 创建对象接受响应信息·
    try:
        # 对浏览器发回的信息进行解码
        response = urllib.request.urlopen(request)  # 打开信息
        html = response.read().decode('utf-8')  # 解码
        # print(html)
    except urllib.error.URLError as e:
        if hasattr((e,'code')):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)

    return html


def saveData(datalist,savepath):
    print('--')
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet('DOUBAN TOP250',cell_overwrite_ok=True)
    col = ('电影详情链接','图片链接','中文名','外文名','评分','评分数','概况','相关信息')
    for i in range(0,8):
        sheet.write(0,i,col[i]) # 列名
    for i in range(0,250):
        print('第{}条'.format(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])  # 数据
    book.save('豆瓣top250.xls')  # 保存


def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"'+data[index]+'"'
        sql = '''
                       insert into movie_250(
                       info_link,pic_link,cname,ename,score,rated,introduction,info)
                       values(%s)
                   ''' % ",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()
def init_db(dbpath):
    sql = '''
        create table movie_250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname nvarchar,
        ename varchar, 
        score numeric,
        rated numeric,
        introduction text,
        info text
        )
    '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()




if __name__ == "__main__":
# 调用函数
    main()
    #init_db("movietest.db")
    print('爬取成功！')
