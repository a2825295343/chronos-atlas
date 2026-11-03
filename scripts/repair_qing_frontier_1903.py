"""Fill sourced gaps around Tianjin and two Himalayan frontier stretches."""
from territory_repair_stage import Stage, read
from shapely.geometry import box, shape
from shapely import union_all

TIANJIN = 'https://openrivers.lib.umn.edu/article/river-conservancy-and-the-undetermined-future-of-the-port-of-tianjin/'
EAST = 'https://arunachalpradesh.gov.in/images/Gazetteer/East-kameng-west-kameng-and-tawang.pdf'
WEST = 'https://searcharchives.bl.uk/catalog/040-000565420'


def main():
    stage = Stage('qing-frontier-gaps-2026-11-03', [18, 19])
    tianjin = box(116.85, 38.68, 118.7, 39.54)
    land = union_all([shape(f['geometry']).intersection(tianjin)
                      for f in read('public/data/ne_10m_land.geojson')['features']])
    for start, end in stage.periods(tianjin, 1900, 1911):
        stage.repair(tianjin, start, end, [
            ('Qing Dynasty', '清朝', 'Q8733', land, TIANJIN,
             '天津租界周边清朝辖地按底图陆地轮廓补绘。沿用已有租界范围，补绘部分不代表精确历史海岸。'),
        ])

    # Existing coverage wins. Show the otherwise blank frontier as a
    # geographical group without assigning the whole stretch to one state.
    frontiers = [
        (box(75.9, 32.4, 80.3, 36.45), 'Western Himalayan Frontier Communities',
         '拉达克—藏西边区', WEST,
         '拉达克与藏西之间的高原边区示意。沿用同年已有政权范围，余下范围作地理集合展示，具体山口和各地管辖边界尚待核定。'),
        (box(92.0, 26.85, 96.45, 28.85), 'Eastern Himalayan Frontier Communities',
         '东喜马拉雅边区诸地方', EAST,
         '不丹以东的边区示意，包含门巴等地方社群活动地区。部分地区与藏传佛教寺院体系有关，各地实际管辖不同。'),
    ]
    for region, name, label, source, note in frontiers:
        for start, end in stage.periods(region, 1895, 1913):
            stage.repair(region, start, end, [
                (name, label, 'local:' + name.lower().replace(' ', '-'), region,
                 source, note, {'regionalCollection': True}),
            ])
    stage.finish('qing-frontier-gaps-review.json')


if __name__ == '__main__':
    main()
