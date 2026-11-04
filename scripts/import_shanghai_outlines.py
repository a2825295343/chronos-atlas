"""Import Shanghai boundaries for labels previously backed only by a seat."""
import sys
import xml.etree.ElementTree as ET

from import_chinese_province_snapshots import DEST, LICENSE, SOURCE, geometry
from import_early_chinese_provinces import shape_of
from territory_repair_stage import clean, read, write
from shapely import union_all
from shapely.geometry import Point, Polygon, mapping

TAG = 'shanghai-historical-outlines'
SEAT = (121.49, 31.22)
COUNTY_MAP = 'https://m.thepaper.cn/baijiahao_27044796'
CITY_MAP = 'https://www.thepaper.cn/newsDetail_forward_1372975'
SHANGHAI_GAZETTEER = 'https://www.shanghai.gov.cn/shanghai/newshanghai/上海通志.pdf'

# The 1928 and 1944 map panels share a 535×600 modern basemap. Trace the
# historical fill only, using the coastline to align the panels to WGS84.
CITY_1928 = [
    (219,320),(228,321),(235,310),(245,312),(243,290),(248,277),(260,274),
    (258,258),(269,252),(272,245),(283,254),(295,247),(303,255),(323,260),
    (334,267),(350,280),(333,283),(329,294),(344,295),(348,314),(337,317),
    (325,317),(303,324),(309,337),(313,349),(310,361),(319,380),(306,387),
    (291,385),(286,394),(291,410),(271,416),(257,425),(244,426),(231,431),
    (229,422),(235,415),(232,399),(241,391),(236,381),(226,358),(220,340),
]
CITY_1944 = [
    (143,249),(152,235),(168,221),(182,224),(192,213),(211,214),(227,202),
    (241,214),(258,221),(276,237),(289,255),(318,260),(339,273),(355,289),
    (369,303),(380,321),(397,344),(410,363),(424,391),(431,414),(438,438),
    (442,451),(437,466),(427,478),(401,479),(378,481),(355,485),(331,491),
    (308,497),(283,496),(268,501),(255,492),(244,496),(241,480),(244,463),
    (235,448),(234,434),(225,427),(224,416),(239,406),(239,394),(252,388),
    (260,376),(251,368),(244,359),(239,354),(228,349),(224,337),(208,334),
    (201,324),(188,321),(183,309),(169,309),(157,301),(150,289),(149,272),
]
ISLANDS_1944 = [
    [(193,83),(205,78),(224,74),(241,79),(263,97),(287,121),(312,137),
     (339,146),(366,158),(391,168),(405,183),(416,196),(423,211),(423,222),
     (416,227),(404,222),(386,212),(365,207),(343,195),(320,187),(294,180),
     (274,169),(252,153),(231,141),(216,125),(202,105)],
    [(242,163),(250,159),(260,161),(267,170),(255,171),(245,168)],
    [(345,247),(356,242),(370,246),(375,253),(369,259),(357,258)],
    [(382,268),(391,266),(399,274),(402,283),(395,286),(386,279)],
    [(407,262),(416,263),(428,269),(435,278),(432,289),(425,293),(416,285),(408,276)],
]
# Separate the two concession footprints, as depicted within the 1928 city.
INTERNATIONAL = [(267,308),(282,309),(292,308),(302,304),(310,302),(318,301),
                 (316,309),(307,313),(299,316),(293,322),(283,321),(274,316)]
FRENCH = [(272,318),(283,321),(293,323),(297,330),(292,336),(280,338),
          (270,333),(265,327)]


def city_trace(points):
    return clean(Polygon([(120.718151 + x * .002702475 - y * .000034400,
                           31.952313 + x * .000027324 - y * .002284214)
                          for x, y in points]))

# Generalized trace of the outer line on the 399×425 reproduction of the
# 1915 map. The old town and the map scale anchor it to the atlas.
COUNTY_TRACE = [
    (50,406),(53,393),(65,377),(64,351),(69,327),(72,312),(90,319),
    (94,304),(107,306),(124,293),(140,291),(136,282),(159,274),(167,270),
    (154,252),(138,255),(130,248),(118,259),(124,244),(119,239),(117,229),
    (110,220),(102,214),(98,214),(99,199),(90,196),(82,187),(76,184),
    (56,187),(53,178),(51,163),(40,160),(49,151),(54,144),(42,139),
    (41,126),(47,126),(61,132),(64,119),(67,114),(61,112),(73,105),
    (82,103),(93,107),(96,121),(103,124),(106,133),(117,143),(127,141),
    (131,136),(148,129),(152,120),(173,114),(185,120),(208,118),(220,110),
    (216,101),(211,91),(218,82),(219,75),(243,66),(274,60),(285,66),
    (291,48),(290,43),(303,30),(315,22),(325,24),(335,34),(338,46),
    (330,51),(341,61),(344,80),(351,86),(350,98),(363,119),(361,137),
    (345,140),(330,140),(319,143),(306,140),(290,147),(273,153),(267,161),
    (262,161),(264,170),(270,180),(264,187),(267,199),(265,211),(273,216),
    (265,218),(258,228),(273,245),(270,249),(254,247),(259,264),(244,263),
    (235,269),(232,258),(223,270),(227,282),(244,276),(250,282),(260,281),
    (275,296),(282,305),(268,310),(263,319),(246,324),(232,322),(228,316),
    (220,319),(207,326),(204,339),(206,359),(208,371),(197,378),(172,386),
    (154,390),(146,397),(124,402),(107,402),(92,408),(79,412),(63,405),
]


def main(city1946, city1952):
    path1946 = next(e for e in ET.parse(city1946).getroot() if e.get('id') == 'layer2')[44]
    svg1952 = next(e for e in ET.parse(city1952).iter() if e.get('id') == 'path1891')
    county = clean(Polygon([(121.49 + (x - 217) * .00105, 31.22 + (160 - y) * .00097)
                            for x, y in COUNTY_TRACE]))
    early = city_trace(CITY_1928)
    occupied_mainland = city_trace(CITY_1944)
    occupied = clean(union_all([occupied_mainland, *map(city_trace, ISLANDS_1944)]))
    international = city_trace(INTERNATIONAL).intersection(early)
    french = city_trace(FRENCH).intersection(early).difference(international)
    concessions = union_all([international, french])
    early = clean(early.difference(concessions))
    occupied_before_handover = clean(occupied_mainland.difference(concessions))
    rows = [
        ('county', '上海县', 1909, 1926, 1915, county, COUNTY_MAP, '县治',
         '据1915年《上海县全境图》外缘描绘，以老城厢和比例尺概化定位，细部位置有误差。'),
        ('special', '上海特别市', 1927, 1929, 1928, early, CITY_MAP, '市址',
         '按1928年接收17市乡后的市域概化描绘。1927年沿用这一近邻年份参照。租界单列。'),
        ('municipality', '上海市', 1930, 1936, 1928, early, CITY_MAP, '市址',
         '1930年改称上海市。使用1928年17区市域作概化参照，租界单列。'),
        ('wartime', '上海市（战时）', 1937, 1937, 1928, early, CITY_MAP, '市址',
         '1937年淞沪会战后日军占领华界，年底设大道政府。用战前市域定位，租界单列。'),
        ('wartime', '上海特别市（占领时期）', 1938, 1942, 1944, occupied_before_handover, CITY_MAP, '市址',
         '1938年改组为伪上海特别市并扩展郊县。采用1944年大陆部分概化定位，未逐年复原郊县范围。租界单列。'),
        ('wartime', '上海特别市（占领时期）', 1943, 1944, 1944, occupied, CITY_MAP, '市址',
         '1943年租界交接后并入市区。按1944年市域图描绘，1943年以该图作概化参考。'),
        ('concession', '上海公共租界', 1927, 1942, 1928, international, CITY_MAP, '',
         '按1928年区划图概化描绘。1941年日军进入租界，1943年办理交接。行政界与同年军事控制分开显示。'),
        ('concession', '上海法租界', 1927, 1942, 1928, french, CITY_MAP, '',
         '按1928年区划图概化描绘，1943年交接后并入市区。'),
        ('municipality', '上海市', 1945, 1948, 1946, shape_of(path1946), SOURCE.format(1946), '市址',
         '1946年区划复原图的市界轮廓，作为这一阶段的参考。'),
        ('municipality', '上海市', 1949, 1949, 1952, geometry(svg1952.get('d')), SOURCE.format(1952), '市址',
         '采用1952年市域快照概化定位1949年上海市。'),
        ('municipality', '上海市', 1954, 1957, 1952, geometry(svg1952.get('d')), SOURCE.format(1952), '市址',
         '1958年大规模划入郊县之前的市域参考，沿用1952年轮廓，年内调整未细分。'),
    ]
    data = read(DEST)
    features = [f for f in data['features'] if f['properties'].get('supplement') != TAG]
    for slug, name, start, end, year, area, source, locator, note in rows:
        if area.is_empty or not area.is_valid:
            raise ValueError((name, start, area.bounds))
        anchor = Point(SEAT) if area.covers(Point(SEAT)) else area.representative_point()
        key = {'county': 'shanghai-county', 'special': 'shanghai-special'}.get(slug, 'shanghai')
        p = dict(id=f'{TAG}:{name if slug == "concession" else slug}:{start}',
                 provinceKey=key if slug != 'concession' else name,
                 label=name, native=name, country='China', validFrom=start, validTo=end,
                 type={'county': '历史县域', 'concession': '租界'}.get(slug, '历史市域'),
                 labelPosition=(anchor.x, anchor.y), boundaryVisible=False, historicalName=True,
                 dataKind='historical-snapshot', sourceYear=year, sourceUrl=source,
                 source='《上海县全境图》' if slug == 'county' else
                 '上海市域变化图解（据上海市地方志办公室资料）' if source == CITY_MAP else 'Milenioscuro 历史行政区划图',
                 accuracy=note, supplement=TAG)
        if locator:
            p['locatorLabel'] = locator
        if source == CITY_MAP:
            p['administrativeChangeSource'] = SHANGHAI_GAZETTEER
        elif slug != 'county':
            p.update(credit='Milenioscuro，底图 TUBS，经配准和转换', license=LICENSE)
        features.append(dict(type='Feature', geometry=mapping(area), properties=p))
    data['features'] = features
    write(DEST, data)


if __name__ == '__main__':
    main(*sys.argv[1:])
