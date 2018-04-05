import requests
from bs4 import BeautifulSoup
import re
import json
import os
import string

# -- private --


# 处理结果,获取学校信息
def handleSchool(r, params):

    result = []

    # 解析响应, 将数据封装进result中
    s = BeautifulSoup(r.text, 'lxml')


    #div = s.find(id='sch_list')
    #div = s.find(id='zsml-list-box')
    div = s.find("div", class_="zsml-list-box")
    try:

        tables = div('table')
#        body = tables('tbody')('tr')
#        body = div.table.tbody.tr
        body = div.table.tbody.find_all("tr")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print (e)

    if body[0]('td')[0].text == '很抱歉，没有找到您要搜索的数据！':
        print('error: 暂时无法获取数据')
        return result


    #提取学校信息的正则表达式
    pattern = re.compile(r'\((?P<id>[0-9]+)\)(?P<name>.+)')

    #数据
    for tr in body:
        tds = tr('td')
        row = []

        # 学校
        schoolstr = tds[0]('a')[0].text
        g = re.match(pattern, schoolstr)
        id = g.group('id')
        name = g.group('name')
        row.append(id)
        row.append(name)
        # 所在地
        addressstr= tds[1].text
        g = re.match(pattern, addressstr)
        id = g.group('id')
        name = g.group('name')
        row.append(id)
        row.append(name)

        # 985,211
        spans = tds[2]('span')
        if len(spans) > 0:
            #985
            flag = '0'
            if not spans[0].text.isspace():
                flag = '1'
            row.append(flag)
            # 211
            flag = '0'
            if not spans[1].text.isspace():
                flag = '1'
            row.append(flag)
        else:
            flag = '0'
            row.append(flag)
            row.append(flag)


        # 是否研究生院
        flag = '0'
        if not tds[3].text.isspace():
            flag = '1'
        row.append(flag)
        # 是否自主划线
        flag = '0'
        if not tds[4].text.isspace():
            flag = '1'
        row.append(flag)
        # 是否博士点
        flag = '0'
        if not tds[5].text.isspace():
            flag = '1'
        row.append(flag)

        result.append(row)

    return result;





# 处理结果,获取专业信息
def handleProfession(r, params):
    result = []


    SCHOOL_CODE = params['school_id']
    SCHOOL_NAME = params['dwmc']


    # 解析响应, 将数据封装进result中
    s = BeautifulSoup(r.text, 'lxml')
#    div = s.find(id='sch_list')
    div = s.find("div", class_="zsml-list-box")
    table = div('table')
#    body = table('tbody')[0]('tr')
    body = div.table.tbody.find_all("tr")

    if body[0]('td')[0].text == '很抱歉，没有找到您要搜索的数据！':
        print('error: 暂时无法获取数据')
        return result

    #提取信息的正则表达式
    pattern = re.compile(r'[^\']+\'(?P<info>[^\']+)?\'.*')
    numpattern = re.compile(r'[^0-9]+(?P<total>[0-9]+)?[^0-9]+(?P<among>[0-9]+)?.*', re.DOTALL)
    idnamepattern = re.compile(r'\((?P<id>\w+)\)(?P<name>.+)')
    exampattern = re.compile(r'[^0-9]+id=(?P<id>[^&]+)&.*')

    teacherpattern = re.compile(u"[\u4e00-\u9fa5]+")

    #数据
    for tr in body:
#        tds = tr('td')
        tds = tr.find_all("td")
        row = []
        # 主键
        rowid = SCHOOL_CODE

        # 院系所名称
        strs = tds[0].text
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        row.append(id)
        row.append(name)

        rowid += id

        # 专业代码名称
        strs = tds[1].text
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        row.append(id)
        row.append(name)

        rowid += id

        # 研究方向
        strs = tds[2].text
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        row.append(id)
        row.append(name)

        rowid += id

        #<td class="ch-table-center">

        tds = tr.find_all("td", {"class" : "ch-table-center"})

        #学习方式
#        learnway =re.sub(['\"','\'','\s'],'', tds[0].text)
        learnway = tds[0].text

#        dro = b'\xe4\xb8\xad\xe6\x96\x87'

        if learnway == '全日制':
            rowid += str(1)
        else:
            rowid += str(0)
        row.append(learnway)
        #

        # 指导教师
#        teacher = re.match(pattern, tds[1].div.span.text)
#        teacher =re.sub(['\"','\'','\s'],'',tds[1].div.span.text)
        teacher = tds[1].div.span.text.strip()

#        row.append(teacher.group('info'))
        row.append(teacher)

        # 拟招生人数
        stus = re.findall(r"\d+", tds[2].script.text)
        if len(stus) == 1:
            total = 0
            among = 0
        else:

            total = stus[0]
            among = stus[1]

        row.append(total)
        row.append(among)
#       pnumgroup = re.match(numpattern, tds[2].script.text)
        # 总人数
#       total = pnumgroup.group('total')
        # 推免
#        row.append(pnumgroup.group('among'))

        # 考试范围
        if len(tds) > 3:
            path = tds[3]('a')[0].get('href')
        else:
            path = ''
        host = 'http://yz.chsi.com.cn'
        link = host + path
        row.append(path)
#        g = re.match(exampattern, path)
#        id = g.group('id')
#        row.append(id)
#        print (id)

        # 跨专业
        if len(tds) > 4:
            path = tds[4]('a')[0].get('href')
        else:
            path = ''
        host = 'http://yz.chsi.com.cn'
        link = host + path
        row.append(link)

        # 备注
#        remark = re.match(pattern, tds[7].script.text)
#        row.append(remark.group('info'))

        if len(tds) > 5:
            remark = tds[5].script.text
            l = remark.find('\'')
            r = remark.rfind('\'')
            remark = remark[l+1:r]
        else:
            remark  = ''
        row.append(remark)
        # 学校名字
        row.insert(0, SCHOOL_NAME)
        # 学校代码
        row.insert(0, SCHOOL_CODE)
        # 主键
        row.insert(0, rowid)
        result.append(row)
    return result;


# 处理结果获取考试范围
def handleExaminations(r, params):
    result = []
    professionid = params['professionid']

    # 解析响应, 将数据封装进result中
    s = BeautifulSoup(r.text, 'lxml')

#    div = s.find(id='result_list')
    div = s.find("div", class_="zsml-result")

    try :
        table = div('table');
#       body = table('tbody')[0]('tr')
        body = div.find_all("tbody", class_="zsml-res-items")
    except Exception as e:
        print (e)
    if len(body) == 0:
        print(PROFESSIONID + '暂无考试范围数据')
        return result

    # 提取信息的正则表达式
    idnamepattern = re.compile(r'(\((?P<id>[-0-9a-zA-z]+)?\)(?P<name>.+)?)?')
    # 数据
    t = 0
    for tr in body:
        tds = tr('td')
        row = []

        t = t + 1
        # 序号
#        seq = tds[0].text
#        seq = t
#        id = params['id'] + seq
#        row.append(id)
#        print (id)
        seq = params['href']
        row.append(str(t) + seq)
        # 政治
        strs = tds[0].text.strip()
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        if not id:
            id = ''
        if not name:
            name = ''
        row.append(id)
        row.append(name)

        # 外语
        strs = tds[1].text.strip()
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        if not id:
            id = ''
        if not name:
            name = ''
        row.append(id)
        row.append(name)

        # 业务课一
        strs = tds[2].text.strip()
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        if not id:
            id = ''
        if not name:
            name = ''
        row.append(id)
        row.append(name)

        # 业务课二
        strs = tds[3].text.strip()
        g = re.match(idnamepattern, strs)
        id = g.group('id')
        name = g.group('name')
        if not id:
            id = ''
        if not name:
            name = ''
        row.append(id)
        row.append(name)

        row.insert(1, professionid)

        result.append(row)
    return result


# 用给定参数爬取网页, 并用给定方法处理
def getData(url, params, fun):
    # 先找出总页数, 再遍历并解析每一页
    result = []

    # 查询数据的页数
    page_total = 1

    # 发起请求, 获得响应
    r = requests.post(url, params=params)
    # 解析响应
    s = BeautifulSoup(r.text, 'lxml')
    # 获取总页数
#    num = s.find(id='page_total')
#    box  = s.find(name="div", attrs={"class":"zsml-page-box"}).get_text()
    box  = s.find(name="div", attrs={"class":"zsml-page-box"})
    s = u' '.join(box.stripped_strings)

    num = s[-4:]
    num = num.strip()
    numk = re.findall(r'^\d*',num)

    page_total = int(re.findall(r'\d*',num)[0])
#    page_total = int(re.find(r'\d*',num))
#    if num:
#        p = re.compile(r'[0-9]+/(?P<num>[0-9]+)')
#        g = re.match(p, num.text)
#        page_totalstr = g.group('num')
#        page_total = int(page_totalstr)

    #print('共有 ' + str(page_total) + ' 页')

    # 遍历每一页
    for pageno in range(1, page_total + 1):

        #print('当前，第 ' + str(pageno) + ' 页')

        params['pageno'] = str(pageno)

        # 发起请求, 获得响应
        r = requests.post(url, params=params)

        # 处理响应
        resultpage = fun(r, params)
        # 将每一页的结果集加入总结果集中
        result.extend(resultpage)
    return result



# -- public --

# 获取省市数据
def getSs():
    try:
        rjson = json.load(open('ss.json', 'r'))
        return rjson
    except FileNotFoundError as e:
        pass

    host = 'http://yz.chsi.com.cn'
    sspath = '/zsml/pages/getSs.jsp'
    url = host + sspath
    r = requests.post(url)
    rjson = []
    try:
        rjson =  r.json()
    except:
#        print('ss')
        return getSs()
    #return rjson
    result = []
    for item in rjson:
        row = []
        code = item['dm']
        name = item['mc']
        row.append(code)
        row.append(name)
        result.append(row)
    json.dump(result, open('ss.json', 'w'))
    return result


# 生成参数
def makeParams(params):
    ssdm=''
    dwmc=''
    mldm=''
    mlmc=''
    yjxkdm=''
    zymc=''
    pageno=''

    school_id = ''

    #封装请求参数
    data = {'ssdm': ssdm, 'dwmc': dwmc, 'mldm': mldm, 'mlmc': mlmc, 'yjxkdm': yjxkdm, 'zymc': zymc, 'pageno': pageno, 'school_id': school_id}
    for key, value in params.items():
        data[key] = value
    return data

# 给定省市获取学校信息
# params schema: {'ssdm':sscode}
def getSchoolFromSS(params):
    urlschool = 'http://yz.chsi.com.cn/zsml/queryAction.do'
    schools = []
    try:
        schools =  getData(urlschool, params, handleSchool)
    except:
        return getSchool()
    #schools = json.load(open('school.json', 'r'))
    return schools

# 获取全部学校信息
def getSchool():
    try:
        schools = json.load(open('school.json', 'r'))
        return schools
    except FileNotFoundError as e:
        pass
    urlschool = 'http://yz.chsi.com.cn/zsml/queryAction.do'
    schools = []
    params = {}
    try:
        schools =  getData(urlschool, params, handleSchool)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print (e)
        return getSchool()
    json.dump(schools, open('school.json', 'w'))
    return schools

# 给定学校信息获取专业信息
# params schema: {'dwmc':schoolname, 'school_id':school_id}
def getProfession(params):
    urlprofession = 'http://yz.chsi.com.cn/zsml/querySchAction.do'
    return getData(urlprofession, params, handleProfession)

# 给定专业信息获取考试范围
# params:{'id':id, 'dwmc':school, 'yxsmc':faculties, 'zymc':profession, 'yjfxmc':resarch_direction}
# school, faculties, profession, resarch_direction :'(' + code ')' + name
def getExaminations(params):
#    urlexaminations = 'http://yz.chsi.com.cn/zsml/kskm.jsp'
    urlexaminations = params['href']
    result = getExamData(urlexaminations, params, handleExaminations)
    return result

def getExamData(url, params, fun):
    result = []
    r = requests.post(url)
    data = fun(r, params)
    result.extend(data)
    return result


