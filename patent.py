import requests
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.firefox.options import Options


def find_tilte(temp_string):
    index_1 = temp_string.find('-')
    index_temp = temp_string.find('\n', index_1+1)
    if(index_temp-index_1 <= 5):
        index_1 = index_temp
    index_2 = temp_string.find('\n', index_1+1)
    string_tilte = temp_string[index_1+1:index_2]
    while(string_tilte[-1] == ' '):
        string_tilte = string_tilte[:-1]
    while ((string_tilte[0] == ' ') or (string_tilte[0] == '-')):
        string_tilte = string_tilte[1:]
    return string_tilte


def find_abstract(temp_string):
    index_description = temp_string.find('description')
    index_content = temp_string.find('content', index_description)
    index_enter1 = temp_string.find('\n', index_content)
    index_enter2 = temp_string.find('\n', index_enter1+1)
    string_abstract = temp_string[index_enter1+1:index_enter2]
    string_abstract.replace("\t", "")
    return string_abstract


def find_contributor(temp_string):
    start = 0
    contributor_arry = []
    index_DC_contributor = temp_string.find('DC.contributor', start)
    while (index_DC_contributor != -1):
        index_content = temp_string.find('content', index_DC_contributor)
        index_colon1 = temp_string.find('\"', index_content)
        index_colon2 = temp_string.find('\"', index_colon1+1)
        string_contributor = temp_string[index_colon1+1:index_colon2]
        string_contributor.replace(" ", "")
        string_temp = str(string_contributor)
        string_help = string_temp.replace(u'\u3000', u' ')
        contributor_arry.append(string_help)
        start = index_colon2
        index_DC_contributor = temp_string.find('DC.contributor', start)
    return contributor_arry


def find_pdf_link(temp_string):
    index_citation_pdf_url = temp_string.find('citation_pdf_url')
    index_content = temp_string.find('content', index_citation_pdf_url)
    index_colon1 = temp_string.find('\"', index_content)
    index_colon2 = temp_string.find('\"', index_colon1+1)
    string_pdf_link = temp_string[index_colon1+1:index_colon2]
    string_pdf_link.replace(" ", "")
    return string_pdf_link


def find_date(temp_string):
    index_dc_date = temp_string.find('DC.date')
    index_content = temp_string.find('content', index_dc_date)
    index_colon1 = temp_string.find('\"', index_content)
    index_colon2 = temp_string.find('\"', index_colon1+1)
    string_date = temp_string[index_colon1+1:index_colon2]
    string_date.replace(" ", "")
    return string_date


def get_patent(id):
    try:
        url = "https://www.uyanip.com/detail?aid="+str(id)
        options = Options()
        driver = Chrome(executable_path='./chromedriver')
        driver.get(url)
        temp = driver.find_elements_by_xpath(
            '//*[@id="item-detail-a-a-wrapper"]/div[2]/div[3]/span[2]/a')
        if(temp.__len__()==0):
            driver.close()
            return None
        patent_id = temp[0].text
        driver.close()
        url = "https://patents.glgoo.top/patent/"+patent_id
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, None, headers=headers)
        temp_string = res.content.decode('utf-8')
        if(res.apparent_encoding != 'utf-8'):
            return None
    except AssertionError as err:
        return None
    res = {}
    # 专利id
    res["patent_id"] = str(patent_id)
    # 专利名称
    tilte = find_tilte(temp_string)
    res["tile"] = tilte
    # 摘要
    abstract = find_abstract(temp_string)
    res["abstract"] = abstract.replace(" ", "")
    # 贡献者
    contributors = find_contributor(temp_string)
    res["contributors"] = contributors[0]
    # 公司
    res["company"] = contributors[-1]
    # 专利pdf链接
    pdf_link = find_pdf_link(temp_string)
    res["pdf_link"] = pdf_link
    # 专利时间
    date = find_date(temp_string)
    res["date"] = date
    return res


def driver_open(url):
    options = Options()
    driver = Chrome(executable_path='./chromedriver')
    driver.get(url)
    patent_id = []
    spans = driver.find_elements_by_xpath(
        '//*[@id="show-0"]/div')
    for i in range(0, spans.__len__(), 1):
        text = spans[i].text
        index_1 = text.find('CN')
        index_2 = text.find(' ', index_1+1)
        patent_id.append(text[index_1:index_2])
    driver.close()
    return patent_id


def make_url(start, end):
    f = open("./patent.txt", "a")
    base1 = "https://www.uyanip.com/result?exp=AND%20GKR:("
    base2 = "-01-01"
    base3 = "%20TO%20"
    base4 = "-01-01)"
    base5 = "%20AND%20ZLLX:("
    base6 = ")&needSlop=&page="
    base7 = "&sort=0&pageSize=40"
    k = 1
    url = base1+str(start)+base2+base3+str(end)+base4 + \
        base5+str(k)+base6+"1"+base7
    options = Options()
    driver = Chrome(executable_path='./chromedriver')
    driver.get(url)
    information = driver.find_elements_by_xpath(
        '//*[@id="wrapper"]/div[3]/div[4]/div/div/a')
    maxpage = int(information[0].text)
    driver.close()
    flag = 0
    j=1
    while(j<=maxpage):
        if(start==1990 and flag==0):
            flag=1
            j=100
        url = base1+str(start)+base2+base3+str(end)+base4 + \
            base5+str(k)+base6+str(j)+base7
        patent_id = driver_open(url)
        for i in patent_id:
            this_patent = get_patent(i)
            if(this_patent is None):
                continue
            print(str(this_patent))
            print(start)
            print(j)
            string_write = str(this_patent)
            string_write = str(string_write.encode())
            f.write(string_write)
            f.write("\n")
        j=j+1
    f.close()


def main():
    i=1990
    while(i<=2019):
        url_array = make_url(i, i+1)
        i=i+1


if __name__ == '__main__':
    main()
