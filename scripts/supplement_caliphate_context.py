"""Source-linked population, conflicts and period names for the atlas."""
from territory_repair_stage import read, write, clean
from shapely import union_all
from shapely.geometry import mapping, shape
from merge_historical_wars import main as merge_wars

TAG = 'caliphates-context-2026-11-03'
BUYID = 'https://www.iranicaonline.org/articles/buyids/'
ABBASID = 'https://www.iranicaonline.org/articles/abbasid-caliphate/'
HAITI = 'https://www.marines.mil/Portals/1/Publications/Dominican%20Republic%20and%20Haiti%20Study_2.pdf'


def population():
    records = {}

    def series(names, label, source, scope, observations):
        for name in names:
            records.setdefault(name, {}).update({
                str(year): dict(population=count, label=label, source=source, scope=scope)
                for year, count in observations.items()
            })

    bahrain = 'https://gulfmigration.grc.net/population-by-nationality-bahraini-non-bahrain-in-dates-of-census-1941-2010/'
    series(['Sheikhdom of Bahrain'], '巴林人口普查', bahrain, '含巴林籍及非巴林籍人口',
           {1941:89970, 1950:109650, 1959:143135, 1965:182203})
    series(['State of Bahrain'], '巴林人口普查', bahrain, '普查时点人口。1971年普查早于当年独立。',
           {1971:216078, 1981:350798, 1991:508037, 2001:650604})
    series(['United States of America', 'United States', 'USA'], '美国历史普查',
           'https://www.census.gov/history/pdf/measuringamerica.pdf',
           '按普查当时辖区及统计口径，早期普查未覆盖所有原住民。',
           {1790:3929214, 1800:5308483, 1810:7239881, 1820:9638453, 1830:12860702,
            1840:17063353, 1850:23191876, 1860:31443321})
    series(['Canada', 'Dominion of Canada'], '加拿大历史普查',
           'https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001701',
           '加拿大统计局历史普查序列，各期统计覆盖随联邦扩展变化。',
           {1871:3508583, 1881:4324810, 1891:4801071, 1901:5345825})
    brazil = 'https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/33495-em-150-anos-conheca-a-historia-que-o-censo-conta'
    series(['Empire of Brazil'], '巴西历史普查', brazil, '帝国时期普查时点人口。', {1872:9930478})
    series(['Brazilian Republic', 'Brazil'], '巴西历史普查', brazil, '共和国时期普查时点人口。', {1890:14333915, 1900:17438434})
    write('public/data/historical-population.json', records)


def regions():
    modern = read('public/data/provinces.geojson')['features']
    lookup = {(f['properties']['country'], f['properties']['native']): f for f in modern}
    data = read('public/data/historical-provinces.geojson')
    data['features'] = [f for f in data['features'] if f['properties'].get('supplement') != TAG]

    def group(slug, country, label, names, start, end, owners, url):
        cells = [lookup[country, name] for name in names.split('|')]
        geometry = clean(union_all([shape(f['geometry']) for f in cells]))
        data['features'].append(dict(type='Feature', geometry=mapping(geometry), properties=dict(
            id=f'{TAG}:{slug}:{start}', label=label, native=label, country=country,
            replaces=[f['properties']['id'] for f in cells], validFrom=start, validTo=end, ownerAny=owners,
            type='历史地理核心', dataKind='historical-geographic-reference', historicalName=True,
            geographicReference=True, boundaryVisible=False, priority='fallback', source='分期地名史料',
            sourceUrl=url, accuracy='现代地理单元合并定位历史核心。边界按当时势力裁切。', supplement=TAG,
        )))

    areas = [
        ('fars','Iran','法尔斯','Fars|Bushehr'),
        ('jibal','Iran','吉巴勒','Hamadan|Kermanshah|Markazi|Esfahan|Lorestan|Qom|Tehran|Alborz'),
        ('khuzistan','Iran','胡齐斯坦','Khuzestan'),
        ('kirman','Iran','克尔曼','Kerman'),
        ('baghdad','Iraq','巴格达与伊拉克中部','Baghdad|Babil|Diyala|Wasit|Karbala\''),
        ('basra','Iraq','巴士拉地区','Al-Basrah|Maysan|Dhi-Qar'),
    ]
    for slug, country, label, names in areas:
        group(slug, country, label, names, 762, 944, ['Abbasid Caliphate'], ABBASID)
        group(slug, country, label, names, 945, 1055, ['Buyid Dynasty'], BUYID)
    group('khurasan','Iran','呼罗珊西部','North Khorasan|Razavi Khorasan|South Khorasan',750,820,['Abbasid Caliphate'],ABBASID)
    constitution = 'https://mjp.univ-perp.fr/constit/ht1806.htm'
    for slug, label, parts in [
        ('haiti-north','北部省',"Nord|Nord-Est|Nord-Ouest"),
        ('haiti-west','西部省','Ouest|Sud-Est'),
        ('haiti-south','南部省',"Sud|Grand'Anse|Nippes"),
        ('haiti-artibonite','阿蒂博尼特省',"L'Artibonite|Centre"),
    ]:
        group(slug, 'Haiti', label, parts, 1807, 1843, ['Divided Haiti','Republic of Haiti'], constitution)
    write('public/data/historical-provinces.geojson', data)


def wars():
    data = read('public/data/historical-wars-supplements.json')
    entries = {row['war']['id']:row for row in data['wars']}

    def add(slug, title, start, end, parties, location, source, cause, result):
        identifier = 'historic-' + slug
        periods = [[start, end]]
        participants = [
            dict(name=label, displayName=label, side=str(side), periods=periods, polityNames=names)
            for side, (label, names) in enumerate(parties, 1)
        ]
        entries[identifier] = {
            'war': {'id':identifier, 'name':title, 'category':'历史战争与战役',
                    'source':'史料补录', 'url':source, 'participants':participants,
                    'periods':periods, 'from':start, 'to':end},
            'detail':dict(id=identifier, title=title, sources=[source], location=location,
                          cause=cause, result=result, supplement=TAG),
        }

    abbasid = ['Abbasid Caliphate']
    add('talas-751','怛罗斯之战',751,751,[('唐朝远征军',['Tang Dynasty']),('阿拔斯军',abbasid)],
        [71.4,42.9], 'https://www.metmuseum.org/it/toah/ht/06/nc',
        '唐朝与阿拔斯势力在中亚的扩张引发交战。','阿拔斯方面获胜，唐军撤退。')
    add('abbasid-brothers','阿明与马蒙的继承战争',811,813,[('阿明与巴格达军',abbasid),('马蒙与呼罗珊军',abbasid)],
        [44.4,33.3], 'https://www.iranicaonline.org/articles/mamun-abul-abbas-abd-allah/',
        '哈伦·拉希德去世后，两位继承人围绕哈里发位和呼罗珊控制权决裂。',
        '马蒙的军队攻克巴格达，阿明被杀。此后地方争乱持续。')
    add('zanj-revolt','赞吉起义',869,883,[('阿拔斯政府军',abbasid),('赞吉起义军',[])],
        [47.8,30.5], 'https://www.iranicaonline.org/articles/basra/',
        '伊拉克南部的被奴役劳动者及其他群体在阿里·本·穆罕默德领导下起事。',
        '起义军一度攻陷巴士拉，阿拔斯军于883年攻克起义中心。')
    add('baghdad-1258','巴格达围城战',1258,1258,[('旭烈兀蒙古军',['Mongol Empire','Ilkhanate']),('阿拔斯巴格达守军',abbasid)],
        [44.4,33.3], 'https://www.iranicaonline.org/articles/il-khanids-i-dynastic-history/',
        '蒙古向西亚扩张，旭烈兀与巴格达哈里发谈判失败后进兵。',
        '巴格达陷落，末代巴格达哈里发穆斯塔辛被杀。')
    add('haiti-north-south','海地南北争战',1807,1810,[('克里斯托夫北方政府',['Divided Haiti']),('佩蒂翁南方政府',['Divided Haiti'])],
        [-72.4,19.1], HAITI, '德萨林遇刺后，北方和南方的政府争夺权力。',
        '主要敌对行动趋于停息，南北仍分治。1820年布瓦耶重归统一。')
    hungary_id = 'hungarian-independence-1848'
    add(hungary_id,'匈牙利革命与独立战争',1848,1849,
        [('匈牙利革命军',['Hungarian Nationalists']),('奥地利帝国',['Austrian Empire'])],
        [21.62,47.53], 'https://mnm.hu/en/en/exhibitions/history-hungary-part-ii/1848-49-revolution-and-war-independence',
        '匈牙利围绕宪政自治及哈布斯堡君主权力与维也纳决裂，1849年宣布独立。',
        '奥军得到俄罗斯帝国军事支援。匈牙利革命军主力于1849年8月投降，同年秋季最后据点结束抵抗。')
    entries['historic-' + hungary_id]['war']['participants'].append(dict(
        name='Russian Empire', displayName='俄罗斯帝国', side='2', periods=[[1849,1849]], polityNames=['Russian Empire']))
    entries['historic-' + hungary_id]['detail']['sources'].append('https://oktober6.kormany.hu/tortenelmi-kronologia')
    northern_id = 'great-northern-war'
    add(northern_id,'大北方战争',1700,1721,
        [('瑞典',['Sweden','Swedish Empire','Kingdom of Sweden']),('俄国',['Tsardom of Russia','Russian Empire'])],
        [34.55,49.59], 'https://riksarkivet.se/resurser/ryssen-kommer',
        '瑞典与俄国、萨克森和丹麦等围绕波罗的海地区的主导权交战。战事扩展至波兰立陶宛，卡尔十二世支持斯坦尼斯瓦夫与奥古斯特二世争夺王位。',
        '1709年瑞典在波尔塔瓦失利，奥古斯特二世重登波兰王位。1721年《尼斯塔德条约》结束俄瑞战争。')
    northern = entries['historic-' + northern_id]
    northern['war']['participants'] += [
        dict(name='Saxony', displayName='萨克森选侯国', side='2', periods=[[1700,1706],[1709,1719]], polityNames=['Electorate of Saxony','Saxony']),
        dict(name='Denmark-Norway', displayName='丹麦—挪威', side='2', periods=[[1700,1700],[1709,1720]], polityNames=['Denmark-Norway','Kingdom of Denmark','Kingdom of Norway']),
        dict(name='Leszczynski faction', displayName='斯坦尼斯瓦夫一世派',
             side='1', periods=[[1704,1709]], polityNames=['Polish-Lithuanian Commonwealth'],
             role='波兰立陶宛联邦内部的亲瑞典派。'),
        dict(name='Augustus II faction', displayName='奥古斯特二世派',
             side='2', periods=[[1704,1706],[1709,1709]], polityNames=['Polish-Lithuanian Commonwealth'],
             role='波兰立陶宛联邦内部与俄国合作的王位竞争方。'),
    ]
    northern['detail']['sources'].append('https://mnk.pl/en/wystawy/stanislaw-leszczynski-i-august-ii-wettin/')
    # Keep the existing war ID for saved links, with the COW coding preserved as provenance.
    resistance_id = 'cow-inter-130'
    resistance_source = 'https://www.ndrc.gov.cn/fggz/fgjh/djzc/202104/t20210429_1278661_ext.html'
    years = [[1937,1945]]
    entries[resistance_id] = {
        'war': dict(id=resistance_id,name='抗日战争（全面抗战）',category='国家间战争',from_=1937,to=1945,
            periods=years,source='历史分期与参战方核查',url=resistance_source,
            scopeNote='此条覆盖1937—1945年中国全面抗战。1931年起的局部抗战另有分期记录。本档列中国战场的主要参战方。',
            participants=[
                dict(name='Empire of Japan',displayName='日本',side='1',periods=years,code='740',
                     polityNames=['Japan','Empire of Japan'],role='侵华日军'),
                dict(name='Republic of China',displayName='中华民国国民政府',side='2',periods=years,code='710',
                     polityNames=['China','Republic of China'],role='国民政府及国民革命军'),
                dict(name='CCP',displayName='中国共产党领导的抗日武装',side='2',periods=years,
                     polityNames=['Communist Party of China'],role='八路军、新四军及其他敌后抗日部队'),
            ]),
        'detail': dict(id=resistance_id,title='抗日战争（全面抗战）',location=[116.21,39.85],
            sideNames=['日本','中国抗日阵营'], reviewedHistorical=True,
            cause='日本持续扩大对中国的侵略。1937年卢沟桥事变后战事扩展，进入全民族抗战阶段。',
            result='中国军民持续抗战。1945年日本宣布接受《波茨坦公告》，9月2日正式签署投降书。',
            sources=[resistance_source,'https://www.mod.gov.cn/gfbw/gfjy_index/16390944.html',
                     'https://history.state.gov/milestones/1937-1945/pearl-harbor',
                     'https://correlatesofwar.org/data-sets/cow-war/']),
    }
    entries[resistance_id]['war']['from'] = entries[resistance_id]['war'].pop('from_')
    data['wars'] = list(entries.values())
    write('public/data/historical-wars-supplements.json', data)
    merge_wars()


if __name__ == '__main__':
    population()
    regions()
    wars()
