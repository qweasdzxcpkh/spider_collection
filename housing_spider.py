import re
import time
import base64
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from io import BytesIO
from fontTools.ttLib import TTFont
from prettytable import PrettyTable
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker

coord_cv_dic = {
    'GlyphCoordinates([(1077, 0),(189, 0),(189, 169),(536, 169),(536, 1345),(180, 1242),(180, 1422),(731, 1582),(731, 169),(1077, 169)])': '1',
    'GlyphCoordinates([(1128, 402),(930, 402),(930, 0),(740, 0),(740, 402),(18, 402),(18, 529),(703, 1549),(930, 1549),(930, 557),(1128, 557),(740, 557),(740, 1206),(740, 1275),(744, 1365),(740, 1365),(726, 1327),(681, 1246),(220, 557)])': '4',
    'GlyphCoordinates([(1048, 0),(106, 0),(106, 170),(556, 619),(742, 805),(868, 1022),(868, 1138),(868, 1270),(720, 1411),(580, 1411),(373, 1411),(185, 1235),(185, 1434),(368, 1575),(611, 1575),(820, 1575),(1062, 1349),(1062, 1158),(1062, 1014),(907, 737),(691, 523),(338, 178),(338, 174),(1048, 174)])': '2',
    'GlyphCoordinates([(91, 744),(91, 1154),(363, 1575),(621, 1575),(1113, 1575),(1113, 781),(1113, 389),(836, -26),(586, -26),(350, -26),(91, 368),(291, 753),(291, 136),(604, 136),(912, 136),(912, 763),(912, 1412),(610, 1412),(291, 1412)])': '0',
    'GlyphCoordinates([(438, 815),(161, 944),(161, 1189),(161, 1360),(421, 1575),(623, 1575),(808, 1575),(1048, 1373),(1048, 1213),(1048, 955),(759, 816),(759, 812),(1098, 690),(1098, 396),(1098, 203),(819, -26),(569, -26),(364, -26),(106, 200),(106, 380),(106, 676),(438, 811),(850, 1190),(850, 1294),(720, 1414),(609, 1414),(505, 1414),(359, 1289),(359, 1192),(359, 998),(602, 897),(850, 1000),(590, 722),(303, 606),(303, 390),(303, 278),(471, 134),(606, 134),(737, 134),(901, 277),(901, 384),(901, 609)])': '8',
    'GlyphCoordinates([(1101, 1481),(495, 0),(292, 0),(868, 1376),(94, 1376),(94, 1549),(1101, 1549)])': '7',
    'GlyphCoordinates([(1018, 1350),(897, 1412),(765, 1412),(564, 1412),(320, 1062),(318, 759),(323, 759),(433, 972),(674, 972),(875, 972),(1115, 710),(1115, 493),(1115, 266),(838, -26),(623, -26),(387, -26),(118, 343),(118, 682),(118, 1092),(471, 1575),(759, 1575),(924, 1575),(1018, 1530),(330, 507),(330, 354),(493, 136),(628, 136),(756, 136),(916, 324),(916, 472),(916, 632),(765, 810),(626, 810),(494, 810),(330, 630)])': '6',
    'GlyphCoordinates([(143, 259),(302, 136),(502, 136),(662, 136),(849, 293),(849, 425),(849, 719),(428, 719),(299, 719),(299, 881),(422, 881),(795, 881),(795, 1157),(795, 1412),(510, 1412),(347, 1412),(203, 1302),(203, 1487),(355, 1575),(558, 1575),(756, 1575),(996, 1368),(996, 1203),(996, 899),(686, 812),(686, 808),(854, 790),(1049, 589),(1049, 439),(1049, 230),(748, -26),(498, -26),(278, -26),(143, 56)])': '3',
    'GlyphCoordinates([(177, 238),(333, 136),(502, 136),(662, 136),(858, 315),(858, 612),(659, 776),(470, 776),(379, 776),(225, 762),(225, 1549),(987, 1549),(987, 1376),(407, 1376),(407, 938),(494, 943),(538, 943),(783, 943),(1057, 695),(1057, 477),(1057, 252),(763, -26),(504, -26),(287, -26),(177, 38)])': '5',
    'GlyphCoordinates([(185, 210),(313, 136),(461, 136),(669, 136),(898, 464),(898, 766),(896, 764),(894, 766),(792, 572),(551, 572),(356, 572),(100, 840),(100, 1054),(100, 1282),(380, 1575),(603, 1575),(834, 1575),(1094, 1212),(1094, 865),(1094, 436),(758, -26),(461, -26),(298, -26),(185, 27),(298, 1079),(298, 923),(458, 740),(599, 740),(721, 740),(887, 907),(887, 1026),(887, 1193),(722, 1412),(587, 1412),(462, 1412),(298, 1222)])': '9'
}

# 9a4b: 1: glyph00002
# 9fa4: 4: glyph00005
# 9f92: 2: glyph00003
# 9ea3: 0: glyph00001
# 9e3a: 8: glyph00009
# 958f: 7: glyph00008
# 993c: 6: glyph00007
# 9fa5: 3: glyph00004
# 9476: 5: glyph00006
# 9f64: 9: glyph00010

engine = create_engine('mysql+pymysql://root:herely@localhost:3306/spider?charset=utf8mb4')
Base = declarative_base()
class House(Base):
    __tablename__ = 'houses'

    id = Column(mysql.INTEGER(unsigned=True), primary_key=True)
    img = Column(mysql.VARCHAR(200, charset='utf8mb4', unicode=True))
    house_type = Column(mysql.VARCHAR(20, charset='utf8mb4', unicode=True))
    desc = Column(mysql.VARCHAR(50, charset='utf8mb4', unicode=True))
    detail_url = Column(mysql.VARCHAR(700, charset='utf8mb4', unicode=True))
    layout = Column(mysql.VARCHAR(50, charset='utf8mb4', unicode=True))
    area_in_miles = Column(mysql.VARCHAR(50, charset='utf8mb4', unicode=True))
    addr = Column(mysql.VARCHAR(100, charset='utf8mb4', unicode=True))
    jjr = Column(mysql.VARCHAR(50, charset='utf8mb4', unicode=True))
    money = Column(mysql.VARCHAR(50, charset='utf8mb4', unicode=True))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()





def script(next_page):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    while True:
        try:
            response = requests.get(next_page, headers=headers).text

            # decode font
            _pat_font = re.compile('&#x[0-9a-f]{4};')
            _pat_font_content = re.compile('data:application/font-ttf;charset=utf-8;base64,(.+?)\)')
            target = _pat_font_content.search(response).group(1)
            if target:
                break
        except:
            pass
    target_deco = base64.decodebytes(bytes(target, 'utf8'))
    tfont = TTFont(BytesIO(target_deco))

    # hex({「unicode」}) => glyf key
    cmap = tfont['cmap'].tables[0].cmap
    cmap_dic = {hex(k): v for k, v in cmap.items()}

    # hex({{「unicode」}}) => [0-9]
    this_dic = dict()
    for k, v in cmap_dic.items():
        this_dic['&#x'+k[2:].lower()+';'] = coord_cv_dic.get(tfont['glyf'][v].coordinates.__str__(), 'unknown')

    # decode html
    result = re.sub(_pat_font, lambda x: this_dic[x.group(0)], response)

    soup = BeautifulSoup(result, features="html.parser")



    # 找出所有房产信息项
    ul = soup.find('ul', {'class': 'listUl'})
    lis = ul.findAll('li')

    # ptable = PrettyTable(['出租方式', '描述', '布局', '面积', '方位信息', '房源', '价格'])
    # ptable.add_row(['---', '---', '---', '---', '---', '---', '---'])
    # 每个房产信息项割分字段并保存
    for li in list(filter(lambda x: x is not None, lis)):
        try:
            # 单图片
            img = li.find('img')['lazy_src']
            # house_type: 出租方式（整租？单间？）
            # desc: 吸睛点描述
            house_type, desc = li.find('h2').get_text().strip().split(' | ')
            # 详细页面的url
            detail = li.find('h2').find('a')['href']
            # 布局、面积
            layout, area_in_miles = li.find('p', {'class': 'room'}).get_text().split()
            # 地址、小区、距地铁 等方位信息
            addr = li.find('p', {'class': 'add'}).get_text().split()
            # 房源信息
            jjr = ' '.join(li.find(None, {'class': ['jjr', 'geren', 'gongyu']}).get_text().split())
            # 价格
            money = li.find('div', {'class': 'money'}).get_text().strip()
            session.add(
                    House(
                        img=img,
                        house_type=house_type,
                        detail_url=detail,
                        layout=layout,
                        area_in_miles=area_in_miles,
                        addr=str(addr),
                        jjr=jjr,
                        money=money
                        )
                    )
            session.commit()
        except Exception as e:
            # 页尾有个分页的li，非房产信息
            # print(li)
            # print(e)
            print(li)
            # raise e
            session.rollback()
            continue

        # ptable.add_row([house_type, desc, layout, area_in_miles, addr, jjr, money])

    # 下一页
    next_page = soup.find('a', {'class': 'next'})['href']
    return next_page
    # print(ptable)
    # print(next_page)


if __name__ == '__main__':
    next_page='https://gz.58.com/chuzu/pn34/'
    while next_page:
        print(next_page)
        next_page = script(next_page)
        time.sleep(1)

