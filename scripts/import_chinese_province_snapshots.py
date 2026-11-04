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
}


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
    features = [f for f in data['features'] if f['properties'].get('supplement') != TAG]
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
            end = 1951 if year == 1950 else until
            features.append(dict(type='Feature', geometry=mapping(area), properties=dict(
                id=f'{TAG}:{slug}:{year}', provinceKey=slug, label=name, native=name,
                country='China', validFrom=year, validTo=end, type='历史省级行政区',
                historicalName=True, boundaryVisible=True, dataKind='historical-snapshot',
                sourceYear=year, source='Milenioscuro 历史行政区划图',
                sourceUrl=SOURCE.format(year), credit='Milenioscuro，底图 TUBS，经配准和转换',
                license=LICENSE, supplement=TAG,
                accuracy=f'边界取自 {year} 年复原图的矢量轮廓，经湖泊控制点配准。相邻年份沿用该快照，精度受原图制约。',
            )))
    data['features'] = features
    write(DEST, data)


if __name__ == '__main__':
    main(sys.argv[1:])
