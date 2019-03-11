'''
猫眼，票房spider
'''
import re
import base64
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from io import BytesIO
from fontTools.ttLib import TTFont
from prettytable import PrettyTable

# ----- 这里只是为了拿到字体坐标特征coord_cv_dic -----
# target = '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'
# target_deco = base64.decodebytes(bytes(target, 'utf8'))
# tfont = TTFont(BytesIO(target_deco))
# coord_cv_dic = dict()
# for glyf_key in tfont['glyf'].keys():
#     print(glyf_key)
#     if glyf_key.startswith('uni'):
#         tmp = tfont['glyf'][glyf_key]
#         dic_key = str(tmp.coordinates).__hash__()
#         print('  '+str(dic_key))
#         coord_cv_dic[dic_key] = glyf_key
# ----- 这里只是为了拿到字体坐标特征coord_cv_dic -----

# 这个字典是每个被篡改的数字字体坐标信息，经过人工对比后把字体的坐标信息记录下来，无论怎么篡改，坐标信息变了渲染的时候也会有问题的
coord_cv_dic = {
    'GlyphCoordinates([(373, 0),(285, 0),(285, 560),(253, 530),(149, 470),(109, 454),(109, 539),(182, 573),(238, 623),(265, 648),(305, 696),(316, 719),(373, 719)])': '1',
    'GlyphCoordinates([(323, 0),(323, 171),(13, 171),(13, 252),(339, 716),(411, 716),(411, 252),(508, 252),(508, 171),(411, 171),(411, 0),(323, 252),(323, 575),(99, 252)])': '4',
    'GlyphCoordinates([(134, 195),(144, 126),(217, 60),(271, 60),(335, 60),(423, 158),(423, 311),(337, 397),(270, 397),(227, 397),(160, 359),(140, 328),(57, 338),(126, 706),(482, 706),(482, 622),(197, 622),(158, 430),(190, 452),(258, 475),(293, 475),(387, 475),(516, 346),(516, 243),(516, 147),(459, 75),(390, -12),(271, -12),(173, -12),(112, 42),(50, 98),(42, 188)])': '5',
    'GlyphCoordinates([(139, 173),(150, 113),(210, 60),(258, 60),(300, 60),(359, 97),(398, 159),(412, 212),(418, 238),(425, 292),(425, 319),(425, 327),(425, 331),(424, 337),(399, 295),(352, 269),(308, 243),(253, 243),(164, 243),(42, 371),(42, 477),(42, 586),(169, 719),(267, 719),(335, 719),(452, 644),(512, 503),(512, 373),(512, 235),(453, 73),(335, -12),(256, -12),(171, -12),(119, 34),(65, 81),(55, 166),(415, 481),(415, 557),(333, 646),(277, 646),(218, 646),(132, 552),(132, 474),(132, 404),(173, 363),(215, 320),(336, 320),(415, 407)])': '9',
    'GlyphCoordinates([(130, 201),(145, 126),(216, 60),(270, 60),(332, 60),(417, 146),(417, 270),(378, 309),(337, 349),(277, 349),(251, 349),(215, 339),(225, 416),(239, 415),(296, 415),(385, 474),(385, 535),(385, 583),(322, 646),(268, 646),(217, 646),(149, 584),(139, 518),(51, 533),(67, 623),(124, 670),(182, 719),(266, 719),(324, 719),(374, 693),(423, 669),(476, 581),(476, 485),(426, 410),(377, 388),(440, 373),(511, 281),(511, 211),(511, 118),(374, -13),(270, -13),(175, -13),(51, 99),(42, 189)])': '3',
    'GlyphCoordinates([(47, 622),(47, 707),(511, 707),(511, 638),(476, 602),(409, 505),(341, 384),(290, 261),(271, 197),(246, 107),(238, 0),(147, 0),(148, 42),(165, 144),(181, 204),(212, 324),(271, 435),(301, 492),(365, 584),(398, 622)])': '7',
    'GlyphCoordinates([(503, 84),(503, 0),(30, 0),(30, 31),(41, 61),(51, 86),(78, 133),(118, 180),(175, 233),(213, 265),(271, 313),(350, 387),(371, 416),(412, 472),(412, 573),(337, 646),(277, 646),(214, 646),(138, 572),(137, 502),(47, 512),(56, 614),(176, 719),(382, 719),(502, 605),(502, 520),(502, 475),(469, 398),(426, 348),(406, 325),(339, 262),(291, 222),(251, 189),(201, 144),(178, 120),(160, 97),(152, 84)])': '2',
    'GlyphCoordinates([(410, 534),(398, 586),(377, 609),(341, 646),(289, 646),(247, 646),(215, 623),(173, 592),(150, 535),(138, 506),(125, 423),(125, 369),(157, 418),(248, 464),(299, 464),(386, 464),(510, 334),(510, 232),(510, 165),(452, 49),(352, -12),(286, -12),(176, -12),(38, 147),(38, 335),(38, 543),(114, 637),(181, 719),(294, 719),(379, 719),(433, 671),(486, 625),(498, 541),(139, 232),(139, 188),(178, 103),(247, 60),(285, 60),(339, 60),(420, 150),(420, 227),(420, 300),(341, 387),(223, 387),(139, 301)])': '6',
    'GlyphCoordinates([(42, 353),(42, 483),(67, 557),(93, 635),(197, 719),(275, 719),(389, 719),(448, 628),(476, 586),(492, 522),(508, 462),(508, 353),(508, 290),(496, 188),(482, 149),(455, 71),(354, -12),(275, -12),(172, -12),(112, 62),(42, 150),(132, 353),(132, 176),(213, 60),(335, 60),(418, 177),(418, 529),(376, 588),(336, 646),(213, 646),(177, 595),(132, 529)])': '0',
    'GlyphCoordinates([(177, 388),(69, 428),(69, 534),(69, 614),(181, 719),(369, 719),(483, 608),(483, 532),(483, 428),(377, 388),(443, 366),(512, 271),(512, 205),(512, 112),(382, -12),(170, -12),(105, 50),(41, 110),(41, 207),(41, 277),(111, 371),(159, 537),(159, 485),(225, 422),(277, 422),(325, 422),(360, 454),(393, 485),(393, 579),(326, 646),(224, 646),(159, 582),(131, 207),(131, 168),(165, 99),(202, 79),(236, 60),(277, 60),(309, 60),(360, 81),(381, 101),(422, 140),(422, 268),(338, 350),(212, 350),(131, 269)])': '8'
}


# 发送请求获取页面
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'piaofang.maoyan.com',
    'Referer': 'https://piaofang.maoyan.com/dashboard',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}


def analyse_by_film(ul):
    lis = ul.find_all('li')
    return list(map(lambda x: str(x), [
        lis[0].b.string, lis[1].i.string,
        lis[2].i.string, lis[3].i.string,
        lis[4].i.string
    ]))

if __name__ == '__main__':
    response = requests.get('https://piaofang.maoyan.com/?ver=normal', headers=headers).text

    # 对加密的数字解密，获得字体
    _pat_font = re.compile('&#x[0-9a-f]{4};')
    _pat_font_content = re.compile('data:application/font-woff;charset=utf-8;base64,(.+?)\)')
    target = _pat_font_content.search(response).group(1)
    target_deco = base64.decodebytes(bytes(target, 'utf8'))
    font = TTFont(BytesIO(target_deco))

    # 构造this_dic, 对动态的字体进行分解坐标特征，这样就可以根据coord_cv_dic进行解密
    this_dic = dict()  # key: 坐标特征，value: 真实数字
    for uniitem in font['glyf'].keys():
        if uniitem.startswith('uni'):
            tmp = font['glyf'][uniitem]
            this_dic['&#x'+uniitem[3:].lower()+';'] = \
                coord_cv_dic.get(str(tmp.coordinates), 'unknown')

    # 获得解密后的html
    result = re.sub(_pat_font, lambda x: this_dic[x.group(0)], response)

    # BeautifulSoup解析html，取信息节点，输出
    ptable = PrettyTable(['片名', '实时票房（万元）', '票房占比', '排片占比', '上座率'])
    ptable.add_row(['------', '---', '---', '---', '---'])

    soup = BeautifulSoup(result)
    ticket_tbody = soup.find(id='ticket_tbody')
    for ul in filter(lambda x: isinstance(x, Tag), ticket_tbody):
        ptable.add_row(analyse_by_film(ul))
    print(ptable)  # or save in db
