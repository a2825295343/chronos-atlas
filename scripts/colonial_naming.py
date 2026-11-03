"""Geographic colonial names must not inherit a modern state's official style."""
PREFIXES={'Portugal':'葡属','Spain':'西属','France':'法属','United Kingdom':'英属','Germany':'德属','Italy':'意属','Netherlands':'荷属','Belgium':'比属'}
def colonial_label(nation,country,fallback):
    if country in ['Taiwan','Republic of China']:
        return PREFIXES.get(nation,'')+'台湾'
    if country in ['China',"People's Republic of China"]:
        if nation=='Portugal':return '葡属澳门'
        if nation=='United Kingdom':return '英国在华租借地'
        return {'Netherlands':'荷兰','Spain':'西班牙','France':'法国','Germany':'德国','Italy':'意大利','Belgium':'比利时'}.get(nation,nation)+'在华据点'
    return fallback
