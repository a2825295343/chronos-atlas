"""Dated seat labels for eight former Chinese provinces."""
from territory_repair_stage import read, write

SOURCE = 'https://mzj.sh.gov.cn/lnb-wsws/20231207/ca2768b4ba7e47d28425081839e01e8c.html'
TAG = 'discontinued-chinese-provinces'

# Province seats locate the names without asserting a surveyed boundary.
ROWS = [
    ('chahar', '察哈尔省', 1928, 1951, (114.88, 40.82), '1952年撤销。'),
    ('pingyuan', '平原省', 1949, 1951, (113.93, 35.30), '1949年设立，驻新乡，1952年撤销。'),
    ('suiyuan', '绥远省', 1928, 1953, (111.67, 40.82), '驻归绥，1954年并入内蒙古自治区。'),
    ('songjiang', '松江省', 1949, 1953, (126.64, 45.75), '与合江省合并后驻哈尔滨，1954年并入黑龙江省。'),
    ('liaodong', '辽东省', 1949, 1953, (124.39, 40.13), '驻安东，1954年合并为辽宁省。'),
    ('liaoxi', '辽西省', 1949, 1953, (121.15, 41.12), '驻锦州，1954年合并为辽宁省。'),
    ('rehe', '热河省', 1928, 1954, (117.94, 40.97), '驻承德，1955年撤销。'),
    ('xikang', '西康省', 1939, 1950, (101.96, 30.05), '此阶段驻康定。'),
    ('xikang-yaan', '西康省', 1951, 1954, (103.00, 29.98), '省治迁雅安，1955年撤销。'),
]


def main():
    path = 'public/data/historical-provinces.geojson'
    data = read(path)
    features = [f for f in data['features'] if f['properties'].get('supplement') != TAG]
    for slug, name, start, end, position, note in ROWS:
        features.append(dict(
            type='Feature', geometry=dict(type='Point', coordinates=position),
            properties=dict(id=TAG + ':' + slug, label=name, native=name, country='China',
                            validFrom=start, validTo=end, type='历史省治定位',
                            boundaryVisible=False, locatorOnly=True, sourceUrl=SOURCE,
                            historicalMapUrl='https://www.loc.gov/item/2006458647/',
                            supplement=TAG, accuracy=note + ' 仅标注省治位置，省界待配准。'),
        ))
    data['features'] = features
    write(path, data)


if __name__ == '__main__':
    main()
