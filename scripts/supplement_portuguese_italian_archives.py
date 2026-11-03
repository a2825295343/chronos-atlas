"""Source-backed Portuguese archives and dated Italian province records."""
from merge_historical_wars import main as merge_wars
from territory_repair_stage import read, write

DATA = 'public/data/'
DYNASTY = 'https://www.infopedia.pt/topicos/dominio-da-cultura/historia-de-portugal/terceira-dinastia'
MARRIAGE = 'https://www.rct.uk/collection/stories/tea-in-the-royal-collection'
CENSUS = 'https://ahpweb.parlamento.pt/Detalhe/?id=99939'
WAR = 'https://assets.exercito.pt/SiteAssets/CmdPess/Livro_Recrutamento/RecrutamentoEx%C3%A9rcitoPortugu%C3%AAs_light.pdf'
MOLISE = 'https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/20056'
ISERNIA = 'https://www.gazzettaufficiale.it/eli/id/1970/02/16/070U0020/sg'


def portugal():
    path = DATA + 'curated-facts.json'
    data = read(path)
    union = data['polities'].setdefault('Q377350', {})
    union.update(label='伊比利亚共主邦联', rulersSource=DYNASTY, rulers=[
        [1581, 1598, '菲利佩一世（西班牙腓力二世）'],
        [1598, 1621, '菲利佩二世（西班牙腓力三世）'],
        [1621, 1640, '菲利佩三世（西班牙腓力四世）'],
    ])
    marriage = dict(id='braganza-stuart-1662', kind='royalMarriage', members=[
        'Kingdom of Portugal', 'Kingdom of England',
    ], title='布拉干萨的凯瑟琳与查理二世', detail='葡萄牙公主凯瑟琳于1662年与英格兰国王查理二世成婚，婚姻延续至查理二世1685年去世。', source=MARRIAGE, **{'from': 1662, 'to': 1685})
    data['relations'] = [r for r in data['relations'] if r['id'] != marriage['id']] + [marriage]
    write(path, data)

    path = DATA + 'historical-population.json'
    data = read(path)
    data.setdefault('Kingdom of Portugal', {})['1864'] = dict(
        population=4286995, label='葡萄牙首次全国人口普查',
        source=CENSUS, scope='法定人口口径，含葡萄牙本土、亚速尔和马德拉。普查时在场人口为4,188,410人。',
    )
    write(path, data)

    path = DATA + 'historical-wars-supplements.json'
    data = read(path)
    entry = next(r for r in data['wars'] if r['war']['id'] == 'historic-portuguese-restoration')
    entry['war']['url'] = WAR
    spanish = entry['war']['participants'][1]['polityNames']
    if 'Kingdom of Spain' not in spanish:
        spanish.append('Kingdom of Spain')
    entry['detail'].update(
        sources=[WAR],
        result='葡萄牙在埃尔瓦什防线（1659年）、阿梅希亚尔（1663年）和蒙特斯克拉罗斯（1665年）击退西军。1668年《里斯本条约》结束战争，西班牙承认葡萄牙独立。',
        commanders=['葡萄牙：若昂四世、阿方索六世时期的葡军，蒙特斯克拉罗斯由坎塔涅德伯爵统率',
                    '西班牙：腓力四世、查理二世时期的西军，蒙特斯克拉罗斯由卡拉塞纳侯爵统率'],
    )
    write(path, data)
    merge_wars()


def italy():
    path = DATA + 'historical-provinces.geojson'
    data = read(path)
    features = data['features']
    names = {"L'Aquila": '拉奎拉', 'Teramo': '泰拉莫', 'Pescara': '佩斯卡拉',
             'Chieti': '基耶蒂', 'Campobasso': '坎波巴索', 'Isernia': '伊塞尔尼亚'}
    if any(f['properties']['id'].endswith('-isernia-1970') for f in features):
        for f in features:
            if 'administrativeChangeSource' in f['properties'] and f['properties']['id'].endswith(('isernia-1970', 'campobasso-1970')):
                f['properties']['administrativeChangeSource'] = ISERNIA
        write(path, data)
        return
    next_snapshot = {p['native']: f for f in features if
                     (p := f['properties']).get('country') == 'Italy' and p.get('sourceYear') == 1971}
    result = []
    for f in features:
        p = f['properties']
        name = p.get('native')
        if p.get('country') != 'Italy' or name not in names or not 1948 <= p.get('validTo', 0) <= 1980:
            result.append(f)
            continue
        end = min(p['validTo'], 1969) if name == 'Campobasso' and p['sourceYear'] == 1961 else p['validTo']
        periods = [(p['validFrom'], min(end, 1947), None),
                   (max(1948, p['validFrom']), min(end, 1963), '阿布鲁齐和莫利塞'),
                   (max(1964, p['validFrom']), end, '莫利塞' if name in ('Campobasso', 'Isernia') else '阿布鲁佐')]
        for start, stop, region in periods:
            if start > stop:
                continue
            props = dict(p, label=names[name], validFrom=start, validTo=stop)
            if start != p['validFrom']:
                props['id'] += f'-{start}'
            if region:
                props.update(parentRegion=region, parentRegionSource=MOLISE)
            result.append(dict(f, properties=props))
    for name in ('Campobasso', 'Isernia'):
        f = next_snapshot[name]
        p = dict(f['properties'], label=names[name], validFrom=1970, validTo=1970,
                 parentRegion='莫利塞', parentRegionSource=MOLISE, administrativeChangeSource=ISERNIA,
                 accuracy='1970年伊塞尔尼亚从坎波巴索分设。以1971年普查省界快照表示该次调整后的范围。')
        p['id'] += '-isernia-1970' if name == 'Isernia' else '-campobasso-1970'
        result.append(dict(f, properties=p))
    data['features'] = result
    write(path, data)


def china():
    path = DATA + 'curated-facts.json'
    data = read(path)
    source = 'https://www.dpm.org.cn/lemmas/243081.html'
    data['polities']['Q333567'] = dict(
        source=source, rulersSource=source, rulers=[[1632, 1644, '李自成']],
        summary='李自成是明末起义军领袖。1644年在西安建立大顺，建元永昌，随后攻入北京。山海关战败后撤出北京，1645年死于湖北。',
        facts=[
            dict(field='government', value='起义军组织，李自成统领所部', **{'from': 1632, 'to': 1643}),
            dict(field='government', value='大顺政权，建元永昌，设政府分理政务', **{'from': 1644, 'to': 1644}),
        ],
    )
    write(path, data)


if __name__ == '__main__':
    portugal()
    italy()
    china()
