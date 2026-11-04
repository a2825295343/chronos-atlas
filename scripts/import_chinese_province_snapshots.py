"""Georeference Milenioscuro's 1950/1952 map paths (CC BY-SA 4.0)."""
import sys
import xml.etree.ElementTree as ET

from territory_repair_stage import clean, read, write
from pyproj import Proj
from shapely import union_all
from shapely.geometry import Polygon, mapping
from shapely.ops import transform
from svgpathtools import parse_path

DEST = 'public/data/historical-provinces.geojson'
TAG = 'chinese-province-snapshots'
SOURCE = 'https://commons.wikimedia.org/wiki/File:China,_administrative_divisions_-_en_-_colored_({}).svg'
LICENSE = 'CC BY-SA 4.0 · https://creativecommons.org/licenses/by-sa/4.0/'
# Equidistant conic fit against eight Natural Earth lake centroids. The
# maximum residual is 0.82 SVG pixels (~4 km) at the fitted controls.
PROJ = Proj(proj='eqdc', lon_0=104.00141490, lat_0=36.18941692,
            lat_1=29.88803879, lat_2=42.49079505, ellps='WGS84')
ROWS = {
    'chahar': ('察哈尔省', '1227', None, 1951),
    'pingyuan': ('平原省', '2151', None, 1951),
    'suiyuan': ('绥远省', '1858', '1858', 1953),
    'songjiang': ('松江省', '2599', '1816', 1953),
    'liaodong': ('辽东省', '1774', '1774', 1953),
    'liaoxi': ('辽西省', '1770', '1770', 1953),
    'rehe': ('热河省', '2069', '1728', 1954),
    'xikang': ('西康省', '1979', '1979', 1954),
    # Municipal enclaves must be assigned before surrounding provinces.
    'beijing': ('北京市', '1251', '967', 1953),
    'tianjin': ('天津市', '973', '973', 1953),
    'shanghai': ('上海市', '1891', '1891', 1953),
    'chongqing': ('重庆市', '925', '925', 1953),
    'nanjing': ('南京市', '1245', None, 1952),
    'hebei': ('河北省', '2076', '2001', 1953),
    'shanxi': ('山西省', '2072', '208', 1953),
    'shandong': ('山东省', '1203', '1878', 1953),
    'henan': ('河南省', '2116', '999', 1953),
    'jilin': ('吉林省', '1992', '1992', 1953),
    'heilongjiang': ('黑龙江省', '2588', '1818', 1953),
    'inner-mongolia': ('内蒙古自治区', '1846', '1846', 1953),
    'yunnan': ('云南省', '1895', '1895', 1953),
    'chuan-dong': ('川东行署区', '2161', None, 1951),
    'chuan-xi': ('川西行署区', '2206', None, 1951),
    'chuan-nan': ('川南行署区', '2209', None, 1951),
    'chuan-bei': ('川北行署区', '2202', None, 1951),
    'sichuan': ('四川省', None, '1868', 1953),
    'su-bei': ('苏北行署区', '2554', None, 1952),
    'su-nan': ('苏南行署区', '2573', None, 1952),
    'jiangsu': ('江苏省', None, '1001', 1953),
}

MODERN_IDS = {
    'beijing': ['CHN-1155'], 'tianjin': ['CHN-1816'], 'shanghai': ['CHN-1819'],
    'chongqing': ['CHN-1154'], 'yunnan': ['CHN-1810'],
    'chuan-dong': ['CHN-1809'], 'chuan-xi': ['CHN-1809'],
    'chuan-nan': ['CHN-1809'], 'chuan-bei': ['CHN-1809'],
    'sichuan': ['CHN-1809'],
    'su-bei': ['CHN-1818'], 'su-nan': ['CHN-1818'], 'jiangsu': ['CHN-1818'],
}
MUNICIPALITIES = {'beijing', 'tianjin', 'shanghai', 'chongqing', 'nanjing'}
JIANGSU_PREDECESSORS = {'nanjing', 'su-bei', 'su-nan'}
SEAT_TAG = 'chinese-province-seat-timeline'
SHANGHAI = 'https://english.shanghai.gov.cn/en-Overview/20231209/05cfb15755fe4cea80a0d3a1d69512e2.html'
BEIJING = 'https://www.bjdsdfz.cn/jcdq.jhtml'
SEATS = [
    ('shanghai-county', '上海县', 1292, 1926, (121.49, 31.22), SHANGHAI, '县治'),
    ('shanghai-special', '上海特别市', 1927, 1929, (121.49, 31.22), SHANGHAI, '市址'),
    ('shanghai', '上海市', 1930, 1936, (121.49, 31.22), SHANGHAI, '市址'),
    ('shanghai', '上海市', 1945, 1949, (121.49, 31.22), SHANGHAI, '市址'),
    ('shanghai', '上海市', 1954, 1957, (121.49, 31.22), SHANGHAI, '市址'),
    ('beiping', '北平特别市', 1928, 1929, (116.40, 39.91), BEIJING, '市址'),
    ('beiping', '北平市', 1930, 1936, (116.40, 39.91), BEIJING, '市址'),
    ('beiping', '北平市', 1945, 1948, (116.40, 39.91), BEIJING, '市址'),
    ('beijing', '北京市', 1949, 1949, (116.40, 39.91), BEIJING, '市址'),
    ('beijing', '北京市', 1954, 1957, (116.40, 39.91), BEIJING, '市址'),
    ('tianjin', '天津市', 1954, 1972, (117.20, 39.13), 'https://www.tj.gov.cn/sq/tjgk/tjls/lsyg/', '市址'),
]


def lonlat(x, y):
    return PROJ((x - 589.88221662) * 1e6 / 216.22796882,
                (501.74395761 - y) * 1e6 / 216.66298742, inverse=True)


def geometry(path):
    # Closed SVG subpaths use the even-odd footprint. Sample the infrequent
    # curves as well as the original vertices.
    result = Polygon()
    for subpath in parse_path(path).continuous_subpaths():
        points = [segment.point(t) for segment in subpath
                  for t in ([0] if type(segment).__name__ == 'Line' else [0, .25, .5, .75])]
        if len(points) >= 3:
            ring = clean(Polygon([(p.real, p.imag) for p in points]))
            result = clean(result.symmetric_difference(ring))
    return clean(transform(lonlat, result))


def main(paths):
    data = read(DEST)
    features = [f for f in data['features'] if f['properties'].get('supplement') not in {TAG, SEAT_TAG}]
    for year, path in zip((1950, 1952), paths, strict=True):
        svg = {el.get('id'): el.get('d') for el in ET.parse(path).iter() if el.get('d')}
        covered = Polygon()
        for slug, (name, first, second, until) in ROWS.items():
            ident = first if year == 1950 else second
            if not ident:
                continue
            area = clean(geometry(svg['path' + ident]).difference(covered))
            if area.is_empty or not area.is_valid:
                raise ValueError((year, slug))
            covered = union_all([covered, area])
            start = 1953 if slug == 'jiangsu' else year
            end = (1952 if slug in JIANGSU_PREDECESSORS else 1951) if year == 1950 else until
            change_source = None
            if slug in JIANGSU_PREDECESSORS or slug == 'jiangsu':
                change_source = 'https://www.dajs.gov.cn/art/2023/5/4/art_123_9721.html'
            elif slug.startswith('chuan-') or slug == 'sichuan':
                change_source = 'https://www.zhongguoguoqing.cn/zsgq/xfz/201904/t20190418_5037719.shtml'
            features.append(dict(type='Feature', geometry=mapping(area), properties=dict(
                id=f'{TAG}:{slug}:{year}', provinceKey=slug, label=name, native=name,
                country='China', validFrom=start, validTo=end, replaces=MODERN_IDS.get(slug, []),
                type='中央直辖市' if slug in MUNICIPALITIES else '省级行署区' if slug.startswith(('chuan-', 'su-')) else '历史省级行政区',
                historicalName=True, boundaryVisible=True, dataKind='historical-snapshot',
                sourceYear=year, source='Milenioscuro 历史行政区划图',
                sourceUrl=SOURCE.format(year), credit='Milenioscuro，底图 TUBS，经配准和转换',
                administrativeChangeSource=change_source,
                license=LICENSE, supplement=TAG,
                accuracy=f'边界取自 {year} 年复原图的矢量轮廓，经湖泊控制点配准。相邻年份沿用该快照，精度受原图制约。',
            )))
        if year == 1952:
            sichuan = next(f for f in reversed(features) if f['properties']['provinceKey'] == 'sichuan')
            merged = clean(union_all([geometry(svg['path1868']), geometry(svg['path925'])])
                           .difference(geometry(svg['path1979'])))
            features.append(dict(type='Feature', geometry=mapping(merged), properties=dict(
                sichuan['properties'], id=f'{TAG}:sichuan:1954', validFrom=1954, validTo=1954,
                replaces=['CHN-1809', 'CHN-1154'],
                accuracy='使用1952年四川与重庆轮廓合并表示1954年重庆降为四川省辖市后的区划，未逐县重建。',
                administrativeChangeSource='https://dfz.cq.gov.cn/fzyd/llyj/202406/t20240620_13309226.html',
            )))
    for slug, name, start, end, position, source, location in SEATS:
        features.append(dict(type='Feature', geometry=dict(type='Point', coordinates=position),
                             properties=dict(id=f'{SEAT_TAG}:{slug}:{start}', provinceKey=slug,
                                             label=name, native=name, country='China', validFrom=start, validTo=end,
                                             locatorOnly=True, locatorLabel=location, boundaryVisible=False,
                                             sourceUrl=source, supplement=SEAT_TAG)))
    data['features'] = features
    write(DEST, data)


if __name__ == '__main__':
    main(sys.argv[1:])
