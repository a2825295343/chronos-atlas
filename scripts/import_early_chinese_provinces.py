"""Import selected Qing and Republic of China maps in their native coordinates."""
import re
import sys
import xml.etree.ElementTree as ET

from import_chinese_province_snapshots import DEST, LICENSE, SOURCE, geometry, lonlat
from territory_repair_stage import clean, read, write
from shapely.geometry import Polygon, mapping
from shapely.ops import transform

TAG = 'early-chinese-province-snapshots'
LIAONING = 'https://www.ln.gov.cn/web/sqgk/lsyg/index.shtml'
HEILONGJIANG = 'https://www.hlj.gov.cn/hlj/c108496/202208/c00_30848054.shtml'
MANCHUKUO = 'https://dfz.jl.gov.cn/zsjl/201606/t20160615_5216385.html'
ROWS = {
    1911: [
        (0, '山西省', 1907, 1913, ['CHN-1805']),
        (1, '直隶省', 1907, 1913, ['CHN-1811']),
        (3, '黑龙江省', 1907, 1930, ['CHN-1839']),
        (4, '吉林省', 1907, 1930, ['CHN-1828']),
        (5, '奉天省', 1907, 1927, ['CHN-1813']),
        (5, '辽宁省', 1928, 1930, ['CHN-1813']),
        (6, '四川省', 1907, 1911, ['CHN-1809', 'CHN-1154']),
        (22, '内蒙古诸盟', 1907, 1911, ['CHN-1838']),
    ],
    1936: [
        (3, '察哈尔省', 1928, 1936, ['CHN-1838']),
        (8, '绥远省', 1928, 1936, []),
        (6, '四川省', 1914, 1938, ['CHN-1809', 'CHN-1154']),
    ],
    1946: [
        (6, '察哈尔省', 1945, 1948, ['CHN-1838']),
        (11, '绥远省', 1945, 1949, []),
        (9, '四川省', 1939, 1949, ['CHN-1809', 'CHN-1154']),
        (40, '西康省', 1939, 1949, []),
    ],
}
SEATS = [
    ('奉天省', (123.43, 41.80)),
    ('吉林省', (126.55, 43.83)),
    ('滨江省', (126.64, 45.75)),
    ('三江省', (130.32, 46.80)),
    ('安东省', (124.39, 40.13)),
    ('锦州省', (121.15, 41.12)),
    ('黑河省', (127.50, 50.25)),
]


def shape_of(element):
    path = element.get('d')
    if path:
        return geometry(path)
    numbers = iter(map(float, re.findall(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)', element.get('points'))))
    return clean(transform(lonlat, Polygon(list(zip(numbers, numbers)))))


def main(paths):
    data = read(DEST)
    features = [f for f in data['features'] if f['properties'].get('supplement') != TAG]
    for (year, rows), path in zip(ROWS.items(), paths, strict=True):
        root = ET.parse(path).getroot()
        layer = next(e for e in root if e.get('id') == 'layer2')
        for index, name, start, end, replaces in rows:
            area = shape_of(layer[index])
            if area.is_empty or not area.is_valid:
                raise ValueError((year, name))
            geographic = name == '内蒙古诸盟'
            props = dict(id=f'{TAG}:{year}:{index}:{start}', label=name, native=name,
                         country='China', validFrom=start, validTo=end, replaces=replaces,
                         type='历史地域' if geographic else '历史省级行政区',
                         historicalName=True, boundaryVisible=not geographic,
                         dataKind='historical-geographic-reference' if geographic else 'historical-snapshot',
                         geographicReference=geographic, sourceYear=year,
                         source='Milenioscuro 历史行政区划图', sourceUrl=SOURCE.format(year),
                         credit='Milenioscuro，底图 TUBS，经配准和转换', license=LICENSE,
                         accuracy=f'采用{year}年复原图轮廓作为该时期的参照；政治控制以同年势力图层为准。',
                         supplement=TAG)
            province_key = {'察哈尔省': 'chahar', '绥远省': 'suiyuan', '西康省': 'xikang'}.get(name)
            if province_key:
                props['provinceKey'] = province_key
            if name in {'奉天省', '辽宁省'}:
                props['administrativeChangeSource'] = LIAONING
            if name == '黑龙江省':
                props['administrativeChangeSource'] = HEILONGJIANG
            features.append(dict(type='Feature', geometry=mapping(area), properties=props))
    for i, (name, position) in enumerate(SEATS):
        features.append(dict(type='Feature', geometry=dict(type='Point', coordinates=position),
                             properties=dict(id=f'{TAG}:seat:{i}', label=name, native=name,
                                             country='China', validFrom=1934, validTo=1936,
                                             type='伪满洲国省治', locatorOnly=True, locatorLabel='省治',
                                             boundaryVisible=False, source='吉林省地方志',
                                             sourceUrl=MANCHUKUO, supplement=TAG)))
    data['features'] = features
    write(DEST, data)


if __name__ == '__main__':
    main(sys.argv[1:])
