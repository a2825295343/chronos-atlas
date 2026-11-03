"""World Bank annual population and nominal GDP, with explicit observation years."""
from download_data import get, DEST
import concurrent.futures, json

def main():
    countries=json.loads(get('https://api.worldbank.org/v2/country?format=json&per_page=400'))[1]
    result={x['id']:{'name':x['name'],'iso2':x['iso2Code'],'capital':x['capitalCity'],'region':x['region']['value'],'income':x['incomeLevel']['value'],'observations':{}} for x in countries if x['region']['id']!='NA'}
    def indicator(code):
        return code,json.loads(get(f'https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000&date=1960:2025'))[1]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for code,rows in pool.map(indicator,['SP.POP.TOTL','NY.GDP.MKTP.CD','MS.MIL.TOTL.P1']):
            field={'SP.POP.TOTL':'population','NY.GDP.MKTP.CD':'gdp','MS.MIL.TOTL.P1':'military'}[code]
            for row in rows:
                iso=row['countryiso3code']
                if iso in result and row['value'] is not None:
                    result[iso]['observations'].setdefault(row['date'],{})[field]=row['value']
    (DEST/'statistics.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Prepared annual indicators for {len(result)} economies.',flush=True)

if __name__=='__main__':main()
