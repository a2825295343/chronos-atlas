"""Do not suppress already established names until an arbitrary 1950 cutoff.

Only names are dated here. Present-day boundaries remain locator references.
"""
import json
from territory_repair_stage import ROOT,read,write
US='https://www.census.gov/dataviz/visualizations/048/508.php'
CA='https://www.canada.ca/en/intergovernmental-affairs/services/provinces-territories.html'
AU='https://www.nma.gov.au/defining-moments/resources/federation'
JP='https://www.ndl.go.jp/modern/e/cha1/description06.html'
ES='https://www.boe.es/gazeta/dias/1833/12/03/pdfs/GMD-1833-154.pdf'
def main():
 dates={};sources={}
 us={'Delaware':1787,'Pennsylvania':1787,'New Jersey':1787,'Georgia':1788,'Connecticut':1788,'Massachusetts':1788,'Maryland':1788,'South Carolina':1788,'New Hampshire':1788,'Virginia':1788,'New York':1788,'North Carolina':1789,'Rhode Island':1790,'Vermont':1791,'Kentucky':1792,'Tennessee':1796,'Ohio':1803,'Louisiana':1812,'Indiana':1816,'Mississippi':1817,'Illinois':1818,'Alabama':1819,'Maine':1820,'Missouri':1821,'Arkansas':1836,'Michigan':1837,'Florida':1845,'Texas':1845,'Iowa':1846,'Wisconsin':1848,'California':1850,'Minnesota':1858,'Oregon':1859,'Kansas':1861,'West Virginia':1863,'Nevada':1864,'Nebraska':1867,'Colorado':1876,'North Dakota':1889,'South Dakota':1889,'Montana':1889,'Washington':1889,'Idaho':1890,'Wyoming':1890,'Utah':1896,'Oklahoma':1907,'New Mexico':1912,'Arizona':1912,'Alaska':1959,'Hawaii':1959,'District of Columbia':1801}
 ca={'Ontario':1867,'Québec':1867,'Nova Scotia':1867,'New Brunswick':1867,'Manitoba':1870,'British Columbia':1871,'Prince Edward Island':1873,'Yukon':1898,'Alberta':1905,'Saskatchewan':1905,'Northwest Territories':1870,'Nunavut':1999,'Newfoundland and Labrador':2001}
 au={'New South Wales':1788,'Western Australia':1829,'South Australia':1836,'Queensland':1859,'Victoria':1851,'Tasmania':1856,'Northern Territory':1911,'Australian Capital Territory':1911,'Jervis Bay Territory':1915}
 modern=read('public/data/provinces.geojson')['features'];rules={}
 for f in modern:
  p=f['properties'];c,n=p['country'],p['native'];start=None;source=None
  if c=='United States of America':start=us.get(n);source=US
  if c=='Canada':start=ca.get(n);source=CA
  if c=='Australia':start=au.get(n);source=AU
  if c=='Japan':start={'Okinawa':1879,'Hokkaidō':1869,'Kagawa':1888,'Miyazaki':1883,'Toyama':1883,'Nara':1887,'Tottori':1881,'Fukui':1881,'Ishikawa':1872,'Miyagi':1872,'Shimane':1871,'Tokyo':1868,'Chiba':1873}.get(n,1872);source=JP
  if c=='Spain'and p['type']in ['Province','Autonomous Community']:start={'Santa Cruz de Tenerife':1927,'Las Palmas':1927,'Ceuta':1995,'Melilla':1995}.get(n,1833);source=ES
  if start is None:continue
  rules[p['id']]={'from':start,'source':source,'label':p['label']}
  if c=='Japan'and n=='Tokyo':rules[p['id']]['label']='东京府'
 # Renames that modern administrative descriptions alone cannot date.
 for f in modern:
  p=f['properties']
  if p['country']=='Canada'and p['native']=='Newfoundland and Labrador':rules[p['id']]['periods']=[{'from':1949,'to':2000,'label':'纽芬兰省'}]
  if p['country']=='Australia'and p['native']=='Tasmania':rules[p['id']]['periods']=[{'from':1825,'to':1855,'label':'范迪门地'}]
 (ROOT/'src/region-established-names.mjs').write_text('export default '+json.dumps(rules,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')
 write('public/data/established-region-names-review.json',dict(reviewedAt='2026-11-02',names=len(rules),sources=[US,CA,AU,JP,ES],method='建立／命名年份只解除名称屏蔽，不宣称现代轮廓是该年的行政界。'))
 print('Established region name dates',len(rules))
if __name__=='__main__':main()
