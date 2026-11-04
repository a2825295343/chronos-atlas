"""Import Shanghai boundaries for labels previously backed only by a seat."""
import sys
import xml.etree.ElementTree as ET

from import_chinese_province_snapshots import DEST, LICENSE, SOURCE, geometry
from import_early_chinese_provinces import shape_of
from territory_repair_stage import clean, read, write
from shapely.geometry import Point, Polygon, mapping

TAG = 'shanghai-historical-outlines'
SEAT = (121.49, 31.22)
COUNTY_MAP = 'https://m.thepaper.cn/baijiahao_27044796'

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
    rows = [
        ('county', '上海县', 1909, 1926, 1915, county, COUNTY_MAP, '县治',
         '据1915年《上海县全境图》外缘描绘，以老城厢和比例尺概化定位，细部位置有误差。'),
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
        if not area.is_valid or not area.covers(Point(SEAT)):
            raise ValueError((name, start, area.bounds))
        p = dict(id=f'{TAG}:{slug}:{start}', provinceKey='shanghai-county' if slug == 'county' else 'shanghai',
                 label=name, native=name, country='China', validFrom=start, validTo=end,
                 type='历史县域' if slug == 'county' else '历史市域', labelPosition=SEAT,
                 locatorLabel=locator, boundaryVisible=False, historicalName=True,
                 dataKind='historical-snapshot', sourceYear=year, sourceUrl=source,
                 source='《上海县全境图》' if slug == 'county' else 'Milenioscuro 历史行政区划图',
                 accuracy=note, supplement=TAG)
        if slug != 'county':
            p.update(credit='Milenioscuro，底图 TUBS，经配准和转换', license=LICENSE)
        features.append(dict(type='Feature', geometry=mapping(area), properties=p))
    data['features'] = features
    write(DEST, data)


if __name__ == '__main__':
    main(*sys.argv[1:])
