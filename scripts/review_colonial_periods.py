"""Remove geographic border slivers and cap colonial labels at independence years."""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
allowed={
 'Portugal':set('Angola|Mozambique|Guinea-Bissau|Cabo Verde|Cape Verde|São Tomé and Príncipe|São Tomé and Principe|Timor-Leste|China|India|Sri Lanka|Malaysia|Indonesia|Brazil|Uruguay'.split('|')),
 'Spain':set('Mexico|Guatemala|Belize|Honduras|El Salvador|Nicaragua|Costa Rica|Panama|Cuba|Dominican Republic|Haiti|Puerto Rico|Colombia|Venezuela|Ecuador|Peru|Bolivia|Chile|Argentina|Paraguay|Uruguay|United States of America|Philippines|Guam|Equatorial Guinea|Western Sahara|Morocco'.split('|')),
 'France':set('Morocco|Algeria|Tunisia|Mauritania|Senegal|Mali|Niger|Chad|Burkina Faso|Benin|Togo|Cameroon|Gabon|Central African Republic|Republic of the Congo|Congo|Guinea|Côte d’Ivoire|Ivory Coast|Madagascar|Comoros|Djibouti|France|Haiti|Saint Lucia|Dominica|Grenada|Saint Kitts and Nevis|United States of America|Canada|New Caledonia|French Polynesia|Vanuatu|Vietnam|Laos|Cambodia|India|Reunion|Mayotte|Guadeloupe|Martinique|French Guiana'.split('|')),
 'United Kingdom':set('Egypt|Sudan|South Sudan|South Africa|Namibia|Botswana|Lesotho|Swaziland|Eswatini|Zimbabwe|Zambia|Malawi|Mozambique|Kenya|Uganda|Tanzania|Somalia|Gambia|The Gambia|Ghana|Nigeria|Sierra Leone|Mauritius|Seychelles|Malta|Cyprus|Gibraltar|India|Pakistan|Bangladesh|Myanmar|Sri Lanka|Malaysia|Singapore|Brunei|China|Nepal|Australia|New Zealand|Papua New Guinea|Fiji|Vanuatu|Solomon Islands|United States of America|Canada|Belize|Guyana|Jamaica|Bahamas|Barbados|Trinidad and Tobago|Saint Lucia|Dominica|Saint Kitts and Nevis|Grenada|Qatar|Bahrain|United Arab Emirates|Kuwait|Yemen|Israel|Palestine|Jordan|Iraq|Oman'.split('|')),
 'Germany':set('Namibia|Tanzania|Cameroon|Togo|Rwanda|Burundi|Ghana|China|Papua New Guinea|Samoa|Micronesia|Marshall Islands|Palau'.split('|')),
 'Italy':set('Libya|Eritrea|Ethiopia|Somalia|China'.split('|')),
 'Netherlands':set('Indonesia|Suriname|Sri Lanka|India|Taiwan|South Africa|Guyana|United States of America|Malaysia|China|Curaçao|Aruba|Sint Maarten'.split('|')),
 'Belgium':set('Democratic Republic of the Congo|Rwanda|Burundi'.split('|'))}
ends={
 ('Spain','Morocco'):1956,('Spain','Equatorial Guinea'):1968,('Spain','Western Sahara'):1975,('Portugal','Brazil'):1822,('Portugal','Uruguay'):1821,('Portugal','Sri Lanka'):1658,('Portugal','Malaysia'):1641,('Portugal','Angola'):1975,('Portugal','Mozambique'):1975,('Portugal','Guinea-Bissau'):1974,('Portugal','Cabo Verde'):1975,('Portugal','São Tomé and Príncipe'):1975,('Portugal','Timor-Leste'):1975,('Portugal','India'):1961,('Portugal','China'):1999,
 ('France','Algeria'):1962,('France','Tunisia'):1956,('France','Morocco'):1956,('France','Guinea'):1958,('France','Mali'):1960,('France','Mauritania'):1960,('France','Senegal'):1960,('France','Niger'):1960,('France','Chad'):1960,('France','Burkina Faso'):1960,('France','Benin'):1960,('France','Gabon'):1960,('France','Republic of the Congo'):1960,('France','Central African Republic'):1960,('France','Vietnam'):1954,('France','Laos'):1954,('France','Cambodia'):1953,('France','Djibouti'):1977,('France','Madagascar'):1960,('France','Comoros'):1975,('France','Haiti'):1804,
 ('United Kingdom','Egypt'):1922,('United Kingdom','Sudan'):1956,('United Kingdom','South Sudan'):1956,('United Kingdom','India'):1947,('United Kingdom','Pakistan'):1947,('United Kingdom','Bangladesh'):1947,('United Kingdom','Myanmar'):1948,('United Kingdom','Sri Lanka'):1948,('United Kingdom','Ghana'):1957,('United Kingdom','Nigeria'):1960,('United Kingdom','Kenya'):1963,('United Kingdom','Uganda'):1962,('United Kingdom','Tanzania'):1961,('United Kingdom','Zambia'):1964,('United Kingdom','Malawi'):1964,('United Kingdom','Guyana'):1966,('United Kingdom','Jamaica'):1962,('United Kingdom','Cyprus'):1960,('United Kingdom','Malta'):1964,
 ('Germany','Namibia'):1915,('Germany','Tanzania'):1918,('Germany','Cameroon'):1916,('Germany','Togo'):1914,('Italy','Ethiopia'):1941,('Italy','Libya'):1943,('Italy','Eritrea'):1941,('Italy','Somalia'):1941,('Netherlands','Indonesia'):1949,('Netherlands','Suriname'):1975,('Netherlands','South Africa'):1806,('Belgium','Democratic Republic of the Congo'):1960}
records=set();excluded=0;count=0
for path in (ROOT/'public/data/temporal').glob('*.geojson'):
 data=json.loads(path.read_text(encoding='utf-8'));rows=[]
 for f in data['features']:
  p=f['properties'];parent=p.get('sovereignName')
  if p.get('territoryType')=='colony':
   country=p['NAME'].split(' Colony - ',1)[-1]
   if p['NAME']=='British India':country='India'
   if p['NAME']=='Portuguese India':country='India'
   if p['NAME']=='Portuguese Macau':country='China'
   if country not in allowed.get(parent,set()):excluded+=1;continue
   end=ends.get((parent,country))
   if end is not None:
    p['validTo']=min(p['validTo'],end)
    if p['validFrom']>p['validTo']:excluded+=1;continue
   if parent=='United Kingdom'and country in ['Sudan','South Sudan']and p['validFrom']>=1899:
    p['displayName']='英埃共管苏丹（'+('北部'if country=='Sudan'else'南部')+'）';p['jointRulers']=['United Kingdom','Kingdom of Egypt'];p['territoryType']='joint-administration'
  century=int(path.stem)
  if p['validTo']<century*100 or p['validFrom']>century*100+99:continue
  records.add(p['sourceRecord']);rows.append(f);count+=1
 path.write_text(json.dumps({'type':'FeatureCollection','features':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
p=ROOT/'public/data/temporal/index.json';index=json.loads(p.read_text(encoding='utf-8'));index['counts']['originalPolityRecords']=12061;index['counts']['polityRecords']=len(records);index['counts']['geographicFragmentsExcluded']=excluded;p.write_text(json.dumps(index,ensure_ascii=False),encoding='utf-8')
print('Retained source records',len(records),'excluded fringe/outdated shard rows',excluded,flush=True)
