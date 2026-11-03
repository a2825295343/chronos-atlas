"""Dated locator cores for eight former Chinese provinces."""
from territory_repair_stage import read, write
from shapely.geometry import Polygon, mapping

SOURCE = 'https://mzj.sh.gov.cn/lnb-wsws/20231207/ca2768b4ba7e47d28425081839e01e8c.html'
TAG = 'discontinued-chinese-provinces'

# Locator cores around documented seats and districts. Exclude uncertain
# fringes and keep the reference outline out of the administrative line layer.
ROWS = [
    ('chahar', '察哈尔省', 1928, 1951, [(112.65,39.65),(114.9,39.85),(115.9,41.15),(115.6,42.6),(113.7,42.65),(112.65,41.1)], '1952年撤销，察南、察北主体归河北，雁北及大同等归山西。'),
    ('pingyuan', '平原省', 1949, 1951, [(113.5,35.18),(114.55,35.05),(116.5,35.0),(116.5,36.05),(115.25,36.55),(114.05,36.15),(113.5,35.7)], '1949年设立，驻新乡。1952年撤销，辖地分归河南、山东。'),
    ('suiyuan', '绥远省', 1928, 1953, [(106.8,40.25),(108.4,39.6),(110.0,39.2),(111.8,39.65),(112.55,41.3),(111.4,42),(108.4,41.5)], '原绥远特别区改省，以归绥为省治。1954年并入内蒙古自治区。'),
    ('songjiang', '松江省', 1949, 1953, [(126.0,45.4),(127.3,44.35),(130.6,44.1),(132.7,46.1),(132.4,47.6),(130.6,47.3),(127.4,46.5)], '此条对应1949年与合江省合并后的阶段，驻哈尔滨。1954年并入黑龙江省。'),
    ('liaodong', '辽东省', 1949, 1953, [(122.15,40.05),(123.8,39.98),(124.45,40.15),(126.0,41.3),(125.8,42.5),(124.8,42.7),(123.4,41.7)], '1949年东北省制调整后的辽东省，驻安东。1954年与辽西等地合并为辽宁省。'),
    ('liaoxi', '辽西省', 1949, 1953, [(120.0,40.0),(121.5,40.75),(122.85,41.0),(123.1,42.8),(122.2,43.45),(121.1,42.65),(120.6,41.55)], '1949年东北省制调整后的辽西省，驻锦州。1954年与辽东等地合并为辽宁省。'),
    ('rehe', '热河省', 1928, 1954, [(116.9,40.8),(118.3,40.35),(119.8,40.65),(120.5,41.65),(120.5,42.65),(119.0,43.4),(117.8,43.35),(117.3,42.4)], '原热河特别区改省，以承德为中心。1955年撤销，分归河北、辽宁和内蒙古。'),
    ('xikang', '西康省', 1939, 1954, [(98.8,28.5),(100.9,27.4),(102.25,27.5),(102.95,29.6),(102.2,30.65),(101.2,31.4),(99.4,31.75),(98.5,30.3)], '1938年底议决设立，年度图从1939年显示。1955年撤销。此轮廓仅定位川西核心范围。'),
]


def main():
    path = 'public/data/historical-provinces.geojson'
    data = read(path)
    features = [f for f in data['features'] if f['properties'].get('supplement') != TAG]
    for slug, name, start, end, outline, note in ROWS:
        features.append(dict(
            type='Feature', geometry=mapping(Polygon(outline)),
            properties=dict(id=TAG + ':' + slug, label=name, native=name, country='China',
                            validFrom=start, validTo=end, type='历史省份定位参考', historicalName=True,
                            geographicReference=True, boundaryVisible=False, priority='fallback',
                            dataKind='historical-geographic-reference', source='上海市民政局区划沿革',
                            sourceUrl=SOURCE, supplement=TAG,
                            accuracy=note + ' 地图按年末建制显示；此区域只作核心位置参考，精确省界待核。'),
        ))
    data['features'] = features
    write(path, data)


if __name__ == '__main__':
    main()
