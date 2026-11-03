"""Reviewed dated offices and territorial archive identities; no office titles as people."""
import argparse,copy,hashlib,json,subprocess,urllib.parse
from territory_repair_stage import ROOT,read,write
from prepare_global_archive_review import human
from enrich_polities import simplify
TAG='persia-gulf-archives-2026-11-02';CACHE=ROOT/'.local/persia-gulf-archives';CACHE.mkdir(exist_ok=True)
IRAN='https://academic.oup.com/edited-volume/34347/chapter/291408604'
GULF='https://u.ae/en/about-the-uae/History'
ROWS=[]
def roster(q,source,role,rows,field='ruler'):
 for title,zh,a,b in rows:ROWS.append(dict(country=q,title=title,label=zh,start=a,end=b,source=source,role=role,field=field))
roster('local:safavid-iran',IRAN,'波斯沙阿（萨法维王室）',[
 ('Ismail I','伊斯迈尔一世',1501,1524),('Tahmasp I','塔赫玛斯普一世',1524,1576),('Ismail II','伊斯迈尔二世',1576,1577),('Mohammad Khodabanda','穆罕默德·胡达班达',1578,1587),('Abbas the Great','阿拔斯一世',1587,1629),('Safi of Persia','萨菲一世',1629,1642),('Abbas II of Persia','阿拔斯二世',1642,1666),('Suleiman I of Persia','苏莱曼一世',1666,1694),('Sultan Husayn','苏丹侯赛因',1694,1722),('Tahmasp II','塔赫玛斯普二世',1722,1732),('Abbas III','阿拔斯三世',1732,1736)])
roster('Q63149558',IRAN,'波斯沙阿（阿夫沙尔王室）',[('Nader Shah','纳迪尔沙',1736,1747),('Adil Shah','阿迪尔沙',1747,1748),('Ebrahim Afshar','易卜拉欣沙',1748,1748),('Shahrokh Shah','沙鲁赫沙',1748,1750),('Shahrokh Shah','沙鲁赫沙',1750,1796)])
roster('Q63149558',IRAN,'纳迪尔军事政权的事实领袖；1736年才正式称沙阿',[('Nader Shah','纳迪尔',1734,1735)])
roster('local:zand-iran','https://www.iranicaonline.org/articles/zand-dynasty/','波斯摄政／实际统治者（桑德家族，非全部自称沙阿）',[
 ('Karim Khan Zand','卡里姆汗',1751,1779),('Zaki Khan Zand','扎基汗',1779,1779),('Abol-Fath Khan Zand','阿布·法特赫汗',1779,1779),('Sadeq Khan Zand','萨迪克汗',1779,1781),('Ali-Morad Khan Zand','阿里·穆拉德汗',1781,1785),('Jafar Khan','贾法尔汗',1785,1789),('Lotf Ali Khan','卢特夫·阿里汗',1789,1794)])
roster('local:qajar-iran',IRAN,'波斯统治者（卡扎尔王室；阿迦1796年正式称沙阿）',[
 ('Agha Mohammad Khan Qajar','阿迦·穆罕默德汗',1789,1797),('Fath-Ali Shah Qajar','法特赫·阿里沙',1797,1834),('Mohammad Shah Qajar','穆罕默德沙',1834,1848),('Naser al-Din Shah Qajar','纳赛尔丁沙',1848,1896),('Mozaffar ad-Din Shah Qajar','穆扎法尔丁沙',1896,1907),('Mohammad Ali Shah Qajar','穆罕默德·阿里沙',1907,1909),('Ahmad Shah Qajar','艾哈迈德沙',1909,1925)])
for slug,rows in [
 ('abu-dhabi',[('Shakhbut bin Sultan Al Nahyan','沙赫布特·本·苏丹·阿勒纳哈扬',1928,1966),('Zayed bin Sultan Al Nahyan','扎耶德·本·苏丹·阿勒纳哈扬',1966,1971)]),
 ('dubai',[('Saeed bin Maktoum bin Hasher Al Maktoum','赛义德·本·马克图姆',1912,1958),('Rashid bin Saeed Al Maktoum','拉希德·本·赛义德',1958,1971)]),
 ('sharjah',[('Sultan bin Saqr Al Qasimi II','苏丹·本·萨克尔二世',1924,1951),('Saqr bin Sultan Al Qasimi','萨克尔·本·苏丹',1951,1965),('Khalid bin Mohammed Al Qasimi','哈立德·本·穆罕默德',1965,1971)]),
 ('ras-al-khaimah',[('Sultan bin Salim Al Qasimi','苏丹·本·萨利姆',1921,1948),('Saqr bin Mohammed Al Qasimi','萨克尔·本·穆罕默德',1948,1971)]),
 ('ajman',[('Rashid bin Humaid Al Nuaimi III','拉希德·本·胡迈德三世',1928,1971)]),
 ('umm-al-quwain',[('Ahmad bin Rashid Al Mualla','艾哈迈德·本·拉希德',1929,1971)]),
 ('fujairah',[('Mohammed bin Hamad Al Sharqi','穆罕默德·本·哈马德·沙尔基',1938,1971)])]:roster('local:trucial-'+slug,GULF,'酋长国统治者；不代表全部停战海岸诸邦',rows)
roster('Q16410','https://digitallibrary.un.org/record/712474','部长会议主席／政府首脑；1956年多次交接',[
 ('Imre Nagy','纳吉·伊姆雷',1953,1955),('András Hegedüs','赫格居什·安德拉什',1955,1956),('Imre Nagy','纳吉·伊姆雷',1956,1956),('János Kádár','卡达尔·亚诺什',1956,1958)],field='headOfGovernment')
roster('local:zanzibar-sultanate','https://qdl.qa/en/historical-profile-oman','桑给巴尔苏丹（1856年继承争议，1861年分治获确认）',[
 ('Majid bin Said of Zanzibar','马吉德·本·赛义德',1856,1870),('Barghash bin Said of Zanzibar','巴尔加什·本·赛义德',1870,1888),('Khalifa bin Said of Zanzibar','哈利法·本·赛义德',1888,1890)])
roster('local:yemen-imamate-1814','https://en.wikipedia.org/wiki/Imams_of_Yemen','也门宰德派伊玛目；地方有竞争者，不代表所有也门地区',[
 ('Al-Mutawakkil Ahmad','穆塔瓦基勒·艾哈迈德',1809,1816),('Al-Mahdi Abdallah','马赫迪·阿卜杜拉',1816,1835)])
roster('local:qasimid-yemen','https://en.wikipedia.org/wiki/Imams_of_Yemen','卡西姆家族伊玛目',[('Al-Mansur Ali I','曼苏尔·阿里一世',1775,1809)])
ALIASES={'Adil Shah':'Adel Shah','Jafar Khan':'Jafar Khan Zand','Sultan Husayn':'Soltan Hoseyn','Khalid bin Mohammed Al Qasimi':'Khalid bin Muhammad Al Qasimi','Khalifa bin Said of Zanzibar':'Khalifah bin Said','Majid bin Said of Zanzibar':'Majid bin Said'}
ALIASES.update({'Maktoum bin Butti bin Suhail':'Maktoum bin Butti Al Maktoum','Rashid bin Maktoum':'Rashid bin Maktoum Al Maktoum'})
roster('local:trucial-abu-dhabi',GULF,'阿布扎比统治者',[('Zayed bin Khalifa Al Nahyan','扎耶德·本·哈利法',1855,1909)])
roster('local:trucial-dubai',GULF,'迪拜统治者',[
 ('Maktoum bin Butti bin Suhail','马克图姆·本·布提',1833,1852),('Saeed bin Butti Al Maktoum','赛义德·本·布提',1852,1859),('Hasher bin Maktoum Al Maktoum','哈舍尔·本·马克图姆',1859,1886),('Rashid bin Maktoum','拉希德·本·马克图姆',1886,1894),('Maktoum bin Hasher Al Maktoum','马克图姆·本·哈舍尔',1894,1906)])
roster('local:trucial-sharjah',GULF,'沙迦及相关卡瓦西姆领地统治者；各地权力并非始终统一',[('Sultan bin Saqr Al Qasimi','苏丹·本·萨克尔',1814,1866)])
roster('local:trucial-ras-al-khaimah',GULF,'哈伊马角统治者',[('Humaid bin Abdullah Al Qasimi','胡迈德·本·阿卜杜拉',1869,1900)])
roster('local:trucial-fujairah',GULF,'富查伊拉统治者；1901年后按地方独立政权列出',[('Hamad bin Abdullah Al Sharqi','哈马德·本·阿卜杜拉',1901,1936)])
roster('local:bahrain-sheikhdom',GULF,'巴林统治者',[('Salman bin Hamad Al Khalifa','萨勒曼·本·哈马德',1942,1961),('Isa bin Salman Al Khalifa','伊萨·本·萨勒曼',1961,1970)])
roster('local:kuwait-sheikhdom',GULF,'科威特统治者',[('Ahmad Al-Jaber Al-Sabah','艾哈迈德·贾比尔·萨巴赫',1921,1950),('Abdullah Al-Salim Al-Sabah','阿卜杜拉·萨利姆·萨巴赫',1950,1960)])

def fetch():
 pool=read('.local/persia-gulf-archives/verified-people.json')if(CACHE/'verified-people.json').exists()else{}
 have={e.get('sitelinks',{}).get('enwiki',{}).get('title')for e in pool.values()}
 names=sorted({ALIASES.get(r['title'],r['title'])for r in ROWS}-have)
 for i in range(0,len(names),25):
  params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='enwiki',titles='|'.join(names[i:i+25]),props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'));p=CACHE/(hashlib.sha1(params.encode()).hexdigest()+'.json')
  if not p.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--retry','2','https://www.wikidata.org/w/api.php?'+params,'--output',str(p)],check=True)
  pool.update({q:e for q,e in json.loads(p.read_bytes())['entities'].items()if human(e)})
 write('.local/persia-gulf-archives/verified-people.json',pool);print('Verified people',len(pool))

def apply():
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');flags=read('public/data/flags.json')
 def entity(q,label,en,source,model=None):
  if q not in facts['entities']:facts['entities'][q]=copy.deepcopy(facts['entities'].get(model,dict(fields={})))
  e=facts['entities'][q];e.update(label=label,en=en,description='按时期核对的政权档案；原始条目身份、现代地理与史料推断分开保留。');e['fields'].pop('instanceOf',None)
  if model and flags['entities'].get(model)and q not in flags['entities']:flags['entities'][q]=copy.deepcopy(flags['entities'][model])
  return e
 for n,q,label,model in [('Safavid Dynasty','local:safavid-iran','萨法维波斯','Q161205'),('Zand Dynasty','local:zand-iran','桑德波斯','Q97629053'),('Qajar Dynasty','local:qajar-iran','波斯','Q189326'),('Imamate of Yemen','local:yemen-imamate-1814','也门伊玛目国','Q1042069'),('Qasimids','local:qasimid-yemen','卡西姆伊玛目国','Q5261548'),('Principality of Chernigov','local:chernigov-principality','切尔尼戈夫公国',None),('Principality of Ryazan','local:ryazan-principality','梁赞公国',None)]:
  entity(q,label,n,IRAN,model);cur['identities'][n]=q
  for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
   labels=read(path);labels[n]=label;write(path,labels)
 for q,zh,model in [('local:kuwait-sheikhdom','科威特','Q817'),('local:bahrain-sheikhdom','巴林','Q398'),('local:zanzibar-sultanate','桑给巴尔苏丹国',None),('local:omani-east-africa','阿曼东非属地',None),('local:rus-unseparated','罗斯诸地',None),('local:shaanxi-resistance-1645','陕南抗清诸军',None)]:entity(q,zh,zh,GULF,model)
 for slug,zh in [('abu-dhabi','阿布扎比'),('dubai','迪拜'),('sharjah','沙迦'),('ras-al-khaimah','哈伊马角'),('ajman','阿治曼'),('umm-al-quwain','乌姆盖万'),('fujairah','富查伊拉')]:entity('local:trucial-'+slug,zh+'酋长国','Sheikhdom of '+slug,GULF)
 def fact(q,field,label,a,b,source,value=None):
  e=facts['entities'][q];e['fields'][field]=[r for r in e['fields'].get(field,[])if r.get('supplement')!=TAG];e['fields'][field].append(dict(value=value or label,label=label,citation=[source],supplement=TAG,**{'from':a,'to':b}))
 for q,a,b in [('local:safavid-iran',1501,1736),('local:qajar-iran',1789,1925)]:
  fact(q,'government','沙阿君主制',a,b,IRAN);fact(q,'religion','十二伊玛目派什叶派伊斯兰教（王朝礼制）',a,b,IRAN)
 fact('local:zand-iran','government','摄政／瓦基勒统治，继承期有多方竞争',1751,1794,IRAN)
 for q,a,b in [('local:yemen-imamate-1814',1814,1872),('local:qasimid-yemen',1636,1809)]:
  fact(q,'government','宰德派伊玛目制',a,b,GULF);fact(q,'religion','伊斯兰教宰德派',a,b,GULF)
 # The regional remainder is not a unified state with a common king.
 e=facts['entities']['local:rus-unseparated'];e['fields']['ruler']=[];e['rulerScopeNote']='未分列的罗斯诸公国地域，不设统一统治者；请查看相邻已分列的具体公国。'
 for field in ['ruler','headOfGovernment']:
  target=facts['entities']['Q157734']['fields'].setdefault(field,[])
  for r in facts['entities'].get('local:albusaidi-oman',{}).get('fields',{}).get(field,[]):
   if not any(x.get('value')==r.get('value')and x.get('from')==r.get('from')and x.get('to')==r.get('to')for x in target):target.append(copy.deepcopy(r))
 # An annual-area collection has military leaders, not a fictitious monarch.
 e=facts['entities']['local:shaanxi-resistance-1645'];e['fields']['ruler']=[dict(value='local:hezhen',label='贺珍',roleLabel='抗清军事领袖之一；非统一国家君主',citation=['https://zh.wikisource.org/wiki/清史稿/卷215'],**{'from':1645,'to':1646}),dict(value='local:sunshoufa',label='孙守法',roleLabel='抗清军事领袖之一；各部关系随战事变化',citation=['https://zh.wikisource.org/wiki/清史稿/卷215'],**{'from':1645,'to':1647})]
 pool=read('.local/persia-gulf-archives/verified-people.json');bytitle={e.get('sitelinks',{}).get('enwiki',{}).get('title'):q for q,e in pool.items()}
 for q,e in pool.items():bytitle.setdefault(e.get('labels',{}).get('en',{}).get('value'),q)
 missing=[r['title']for r in ROWS if r['title']not in bytitle and ALIASES.get(r['title'],r['title'])not in bytitle]
 if missing:raise ValueError('Unresolved exact identities: '+str(sorted(set(missing))))
 for q in {r['country']for r in ROWS}:
  for field in {r['field']for r in ROWS if r['country']==q}:facts['entities'][q]['fields'][field]=[r for r in facts['entities'][q]['fields'].get(field,[])if r.get('supplement')!=TAG]
 appointments=[]
 for r in ROWS:
  q=bytitle.get(r['title'])or bytitle[ALIASES[r['title']]];e=pool[q]
  def years(prop):return[int(v['value']['time'][:5])for c in e.get('claims',{}).get(prop,[])if(v:=simplify(c))and isinstance(v['value'],dict)and'time'in v['value']]
  if any(y>r['end']for y in years('P569'))or any(y<r['start']for y in years('P570')):raise ValueError('Identity/reign mismatch '+r['title'])
  row=dict(value=q,label=r['label'],roleLabel=r['role'],at=None,rank='preferred',supplement=TAG,citation=[r['source'],'https://www.wikidata.org/wiki/'+q],**{'from':r['start'],'to':r['end']});facts['entities'][r['country']]['fields'][r['field']].append(row);facts['labels'][q]=r['label'];appointments.append(dict(country=r['country'],field=r['field'],**row))
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur);write('public/data/flags.json',flags)
 # Country headings and IDs must agree in both the map worker and archives.
 names={'Safavid Dynasty':('萨法维波斯','local:safavid-iran'),'Qajar Dynasty':('波斯','local:qajar-iran'),'Zand Dynasty':('桑德波斯','local:zand-iran')}
 for century in [15,16,17,18,19]:
  path=f'public/data/temporal/{century}.geojson';db=read(path);changed=False
  for f in db['features']:
   p=f['properties']
   if p['NAME']in names:
    zh,q=names[p['NAME']];p.update(sourceQid=p.get('sourceQid',p['qid']),qid=q,entityId=q,displayName=zh);changed=True
  if changed:write(path,db)
 write('public/data/persia-gulf-archives-review.json',dict(reviewedAt='2026-11-02',appointments=appointments,people=len({r['value']for r in appointments}),limitations=['非穷尽的全球君主数据库；若没有有界任期，不把现代人物或头衔外推到古代。','停战诸酋长国早期领袖和部分小附属地区仍未完整整理。']))
 print('Added dated offices',len(appointments))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['fetch','apply']);args=p.parse_args();globals()[args.stage]()
