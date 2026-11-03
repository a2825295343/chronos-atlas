"""Resolve war actor aliases and supplement dated North/South Vietnam offices."""
import hashlib,json,subprocess,urllib.parse,unicodedata
from territory_repair_stage import ROOT,read,write
from prepare_global_archive_review import human
TAG='vietnam-war-context-2026-11-02';CACHE=ROOT/'.local/vietnam-war-context';CACHE.mkdir(exist_ok=True)
HO='https://vietnam.gov.vn/president-ho-chi-minh-68961'
TON='https://kln-bacton.angiang.gov.vn/cdvsncttdt'
LIST='https://en.wikipedia.org/wiki/List_of_heads_of_state_of_Vietnam'
PM='https://chinhphu.vn/thanh-vien-chinh-phu-qua-cac-thoi-ky-68352?governId=608&lang=en'
ROWS=[('Q172640','ruler','Ho Chi Minh','胡志明',1945,1945,'临时政府主席',HO),('Q172640','ruler','Ho Chi Minh','胡志明',1946,1969,'国家主席',HO),('Q172640','ruler','Tôn Đức Thắng','孙德胜',1969,1976,'国家主席；1969年继任，1976年统一后职位另属社会主义共和国',TON),('Q172640','headOfGovernment','Ho Chi Minh','胡志明',1945,1955,'政府主席／总理',PM),('Q172640','headOfGovernment','Phạm Văn Đồng','范文同',1955,1976,'总理；此处仅列北越时期',PM),('Q180573','ruler','Ngô Đình Diệm','吴廷琰',1955,1963,'总统',LIST),('Q180573','ruler','Dương Văn Minh','杨文明',1963,1964,'国家元首；年内军政府职务多次调整',LIST),('Q180573','ruler','Phan Khắc Sửu','潘克丑',1964,1965,'国家元首',LIST),('Q180573','ruler','Nguyễn Văn Thiệu','阮文绍',1965,1967,'国家领导委员会主席；1967年任总统',LIST),('Q180573','ruler','Nguyễn Văn Thiệu','阮文绍',1967,1975,'总统；1975年4月辞职',LIST),('Q180573','ruler','Trần Văn Hương','陈文香',1975,1975,'1975年4月21日至28日任总统',LIST),('Q180573','ruler','Dương Văn Minh','杨文明',1975,1975,'1975年4月28日至30日任总统',LIST)]
def main():
 def normal(n):return''.join(c for c in unicodedata.normalize('NFD',n)if not unicodedata.combining(c)).translate(str.maketrans({'Đ':'D','đ':'d'}))
 names={r[2]for r in ROWS};names|={normal(n)for n in names}
 params=urllib.parse.urlencode(dict(action='wbgetentities',format='json',sites='enwiki',titles='|'.join(sorted(names)),props='labels|claims|sitelinks',languages='zh-hans|zh|en',redirects='yes'))
 cache=CACHE/(hashlib.sha1(params.encode()).hexdigest()+'.json')
 if not cache.exists():subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--retry','2','https://www.wikidata.org/w/api.php?'+params,'--output',str(cache)],check=True)
 pool={q:e for q,e in json.loads(cache.read_bytes())['entities'].items()if human(e)};bytitle={normal(e.get('sitelinks',{}).get('enwiki',{}).get('title','')):q for q,e in pool.items()};(CACHE/'verified-people.json').write_text(json.dumps(pool,ensure_ascii=False),encoding='utf8')
 facts=read('public/data/polity-facts.json');review=[]
 for country in ['Q172640','Q180573']:
  for field in ['ruler','headOfGovernment']:facts['entities'][country]['fields'][field]=[r for r in facts['entities'][country]['fields'].get(field,[])if r.get('supplement')!=TAG]
 for country,field,title,label,a,b,role,source in ROWS:
  q=bytitle.get(normal(title))
  if not q:raise ValueError('Unresolved human '+title)
  row={'value':q,'label':label,'from':a,'to':b,'at':None,'roleLabel':role,'rank':'preferred','citation':[source,'https://www.wikidata.org/wiki/'+q],'supplement':TAG};facts['entities'][country]['fields'][field].append(row);facts['labels'][q]=label;review.append({'country':country,'field':field,**row})
 facts['entities']['Q172640']['rulerScopeNote']='国家主席与总理按职务分列；国家元首名单不等于对党内领导层、军事指挥和实际决策者的完整描述。'
 facts['entities']['Q180573']['rulerScopeNote']='年内政变和交接可能先后出现多名元首；军政府期间的总理、军政主导者等尚未完整整理，不以一条总统名单代替全部实际权力关系。'
 write('public/data/polity-facts.json',facts)
 details=read('public/data/war-details.json');v=next(w for w in details['wars']if w['id']=='cow-inter-163')
 v['extraParticipants']=[p for p in v.get('extraParticipants',[])if p.get('supplement')!=TAG]+[dict(name='National Liberation Front of South Vietnam',side='1',sameSideAs='North Vietnam',periods=[[1965,1975]],role='南方民族解放阵线／越共武装；与北越阵营统计可能重叠，不另加一份全国兵力',supplement=TAG)]
 v['sources']=list(dict.fromkeys([*v.get('sources',[]),'https://media.defense.gov/2021/Jun/29/2002751424/-1/-1/0/SPARTANS_IN_DARKNESS.PDF']))
 if not any(w['id']=='cow-inter-170'for w in details['wars']):details['wars'].append({'id':'cow-inter-170'})
 laos=next(w for w in details['wars']if w['id']=='cow-inter-170');laos.update(title='老挝内战（国际化阶段）',mergeUcdp='ucdp-262',cause='老挝王国、巴特寮及其支持力量围绕政权与地区控制冲突，越南战争与国际军事介入使内战延续。1962年中立安排未终止全部战事。',result='1973年万象停火与联合政府安排暂时改变冲突阶段；1975年巴特寮最终掌权。UCDP的老挝政权冲突定义覆盖更长时期，不能把这个阶段的起止当作其全部历史。',sources=['https://history.state.gov/milestones/1961-1968/laos-crisis'],location=[102.6,18])
 write('public/data/war-details.json',details);write('public/data/vietnam-war-context-review.json',dict(reviewedAt='2026-11-02',appointments=review,people=len(pool),notes=['北越“Vietnam”与UCDP“Vietnam (North Vietnam)”按年份合并，避免重复计算同一方。','民族解放阵线独立列出，但不与北越全国军力重复相加。','老挝国际化阶段与UCDP同年冲突合并展示，保留两个来源的定义差异。']))
 print('Vietnam office terms',len(review),'people',len(pool))
if __name__=='__main__':main()
