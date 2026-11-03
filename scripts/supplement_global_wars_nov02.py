"""Add early wars and enrich existing modern definitions without duplicate cards."""
from territory_repair_stage import read,write
TAG='global-wars-2026-11-02'

def main():
 db=read('public/data/historical-wars-supplements.json');rows={r['war']['id']:r for r in db['wars']};added=[]
 def war(slug,title,periods,left,right,cause,result,location,sources,commanders=(),merge=None):
  ident='historic-'+slug
  actors=[dict(name=n,side=s,periods=ps,polityNames=aliases)for s,group in [('1',left),('2',right)]for n,aliases,ps in group]
  scope='按参战时期分别列出主要交战方；年内先后行动不等于同时作战。未收录的盟军不据此判定未参战；不从战争起止自动生成精确占领线。'
  w=dict(id=ident,name=title,category='历史战争与区域战争群',source='2026-11-02有来源补录',url=sources[0],periods=periods,participants=actors,scopeNote=scope,**{'from':periods[0][0],'to':periods[-1][1]})
  d=dict(id=ident,title=title,cause=cause,result=result,location=location,sources=sources,commanders=list(commanders),scopeNote=scope,strengthAssessment='未取得同一战区、同一日期且口径可比的双方兵力；不以全国人口、伤亡或未经核实的传说数字代替。')
  if merge:d['mergeUcdp']=merge
  rows[ident]=dict(war=w,detail=d);added.append(ident)
 kh=[[993,993],[1010,1011],[1018,1019]]
 war('goryeo-khitan','高丽—契丹战争',kh,[('高丽',['Goryeo'],kh)],[('辽朝',['Liao Dynasty','Liao'],kh)],'辽与高丽围绕边境、对宋关系及地区秩序发生冲突，分三轮大规模入侵。','高丽保留王国，接受与辽的外交朝贡安排；1019年龟州战役后进入较稳定关系，不能把993—1019年全部视作连续交战。',[126,39],['https://db.history.go.kr/goryeo/'],['成宗、显宗','萧逊宁、辽圣宗、萧排押','徐熙、杨规、姜邯赞'])
 im=[[1592,1598]]
 war('imjin','壬辰战争（日本侵朝战争）',im,[('朝鲜',['Joseon'],im),('明朝援军',['Ming Dynasty'],[[1592,1593],[1597,1598]])],[('丰臣政权',['Toyotomi Government','Toyotomi Regime','Warring States Japan','Japanese clan - Toyotomi'],im)],'丰臣秀吉要求借道朝鲜进攻明朝，遭拒后发动入侵；朝鲜抵抗与明朝援军介入。','1593年后进入谈判和军事对峙，1597年日军再次大举入侵；秀吉死后日军1598年撤退，朝鲜遭受严重破坏。',[128,36],['https://www.museum.go.kr/ENG/contents/E0201040200.do','https://sillok.history.go.kr/main/main.do'],['朝鲜宣祖、李舜臣、权慄','李如松、陈璘、邢玠','丰臣秀吉、小西行长、加藤清正'])
 for slug,title,ps,enemy,cause,result in [
  ('later-jin-joseon','后金第一次侵朝战争',[[1627,1627]],['Later Jin','Later Jin Dynasty'],'后金要求朝鲜改变亲明立场，边疆安全、毛文龙军事活动和朝鲜内部政局使矛盾加剧。','双方缔结兄弟关系安排，朝鲜尚未在本轮彻底中断对明关系。'),
  ('qing-joseon','清第二次侵朝战争',[[1636,1637]],['Qing Dynasty'],'朝鲜拒绝承认皇太极称帝，清要求改变双方关系并终止朝鲜亲明政策。','仁祖在南汉山城被围后降服，清朝宗藩关系确立；王室质子、贡赋等安排产生长期影响。')]:
  war(slug,title,ps,[('朝鲜',['Joseon'],ps)],[('后金／清军',enemy,ps)],cause,result,[127,37.5],['https://sillok.history.go.kr/main/main.do','https://www.museum.go.kr/ENG/contents/E0201040200.do'],['朝鲜仁祖','皇太极'])
 for slug,title,ps,siam,cause,result in [
  ('burma-siam-1765','缅暹战争与阿瑜陀耶陷落',[[1765,1767]],['Ayutthaya Kingdom'],'贡榜王朝扩大对暹罗与周边地区的军事压力，从南北两路进攻阿瑜陀耶。','1767年阿瑜陀耶陷落，原王权瓦解；达信随后建立吞武里政权，缅军并未长期有效控制整个暹罗。'),
  ('burma-siam-1785','缅暹九军战争',[[1785,1786]],['Rattanakosin Kingdom'],'缅甸波道帕耶试图以多路军队攻灭新建立的曼谷王权，双方争夺边境与地区优势。','暹罗军击退主要进攻，曼谷王权巩固；后来的缅暹战争属于其他轮次。')]:
  war(slug,title,ps,[('缅甸贡榜王朝',['Konbaung Dynasty'],ps)],[('暹罗',siam,ps)],cause,result,[99.5,15],['https://www.thaiembassy.at/en/content_page/item/18-thailands-history.html','https://en.wikipedia.org/wiki/'+('Burmese%E2%80%93Siamese_War_(1765%E2%80%931767)'if slug.endswith('1765')else'Burmese%E2%80%93Siamese_War_(1785%E2%80%931786)')])
 h=[[1791,1804]]
 war('haitian-revolution','海地革命',h,[('圣多明各反奴隶制与独立力量',['Haiti','Saint-Domingue'],h)],[('法国殖民军及远征军',['France','French First Republic','French Consulate','First French Empire','France Colony - Haiti'],h)],'奴隶制、殖民种族等级与法国革命引起的政治动员共同推动起义，随后牵涉殖民军、地方精英和多方国际干预。','废奴、内战和对外战争分阶段进行；1804年海地独立。杜桑·卢维杜尔等力量曾改变对法关系，此为过程总览，不能把13年压成始终固定的两国战争。',[-72.3,19],['https://history.state.gov/milestones/1784-1800/haitian-rev'],['杜桑·卢维杜尔、让-雅克·德萨林','勒克莱尔、罗尚博'])
 n=[[1845,1846]]
 war('nz-northern','新西兰北方战争',n,[('英国及殖民政府军与毛利盟军',['United Kingdom','United Kingdom of Great Britain and Ireland','United Kingdom Colony - New Zealand','New Zealand'],n)],[('赫克与卡维蒂等毛利力量',['Māori','Maori'],n)],'《怀唐伊条约》后主权解释、殖民经济与地方权力冲突激化，赫克多次砍倒旗杆后发生武装战争。','1846年鲁阿佩卡佩卡战事后本轮战争结束；毛利各部立场不同，不把所有毛利人视为一个敌对阵营。',[174.1,-35.4],['https://nzhistory.govt.nz/page/history-new-zealand-1769-1914','https://www.doc.govt.nz/our-work/heritage/heritage-topics/new-zealand-wars/'],['霍内·赫克、特·鲁基·卡维蒂','塔马蒂·瓦卡·内内（英国一方毛利盟友）'])
 o=[[1954,1955],[1957,1959]]
 war('jebel-akhdar','阿曼内战与绿山战争',o,[('马斯喀特和阿曼苏丹国',['Sultanate of Muscat and Oman','Oman'],o),('英国军事介入',['United Kingdom'],[[1957,1959]])],[('阿曼伊玛目政权与抵抗军',['Imamate of Oman'],o)],'苏丹政权与内陆伊玛目政权围绕自治、领土控制与石油勘探冲突；1954—1955年进军后，1957年内陆抵抗再起。','1959年初英军与苏丹军夺取绿山高地，伊玛目领袖流亡；不把UCDP仅达到其统计门槛的1957年误作全部战争时段。',[57.6,23],['https://www.rafmuseum.org.uk/research/online-exhibitions/an-enduring-relationship-a-history/oman-and-the-cold-war/','https://findingaids.library.nyu.edu/nyuad/ad_mc_151/contents/aspace_357315c58e213024d641a72212dcdfa6/'],['赛义德·本·泰穆尔','加利卜·本·阿里·希纳伊、塔利卜·本·阿里'],merge='ucdp-258')
 # France's relationship with the revolution changed. Do not keep it on
 # the opposing side through Toussaint's service to the French Republic.
 haitian=rows['historic-haitian-revolution']['war']['participants']
 haitian[1]['periods']=[[1791,1793],[1802,1804]]
 haitian.extend([
  dict(name='法国共和国军（与革命力量合作阶段）',side='1',periods=[[1794,1801]],polityNames=['French First Republic','French Directory','French Consulate']),
  dict(name='英国干预军',side='2',periods=[[1793,1798]],polityNames=['Kingdom of Great Britain']),
  dict(name='西班牙干预军',side='2',periods=[[1793,1795]],polityNames=['Spanish Empire','Kingdom of Spain']),
  dict(name='里戈派（刀战阶段）',side='2',periods=[[1799,1800]],polityNames=[]),
 ])
 # Use the same actor identities as UCDP at the 1957 overlap. Chinese
 # display labels must not become additional belligerents or flip sides.
 oman=rows['historic-jebel-akhdar']['war']['participants']
 for actor,name in zip(oman,['Oman','United Kingdom','State of Oman/Free Oman']):actor['name']=name
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  labels=read(path);labels['State of Oman/Free Oman']='阿曼伊玛目政权与抵抗军';write(path,labels)
 db['wars']=list(rows.values());write('public/data/historical-wars-supplements.json',db)
 from merge_historical_wars import main as merge
 merge()
 # At the UCDP overlap use the same sourced explanation, not a second card.
 details=read('public/data/war-details.json');byid={r['id']:r for r in details['wars']};byid['ucdp-258']={**rows['historic-jebel-akhdar']['detail'],'id':'ucdp-258'}
 byid['cow-extra-380']={**byid.get('cow-extra-380',{}),'id':'cow-extra-380','title':'英祖战争（1879）','reviewedHistorical':True,'cause':'英国扩张南部非洲控制，向祖鲁王提出难以接受的最后通牒后发动入侵。','result':'英军早期在伊散德尔瓦纳受挫，随后夺取乌伦迪；祖鲁王国被分割，后续内战和殖民吞并另属后续阶段。','location':[31.4,-28.3],'sources':['https://www.nam.ac.uk/explore/zulu-war'],'commanders':['塞奇瓦约、恩钦格瓦约·科萨','切姆斯福德、加内特·沃尔斯利']}
 details['wars']=list(byid.values());write('public/data/war-details.json',details)
 conflict=read('public/data/conflicts.json')
 for w in conflict['wars']:
  if w['id']=='cow-extra-380':
   for p in w['participants']:
    if 'Zulu'in p['name']:p['polityNames']=list(dict.fromkeys([*p.get('polityNames',[]),'Zulu Kingdom','Zululand']))
 write('public/data/conflicts.json',conflict)
 write('public/data/global-wars-nov02-review.json',dict(reviewedAt='2026-11-02',added=added,enriched=['ucdp-258','cow-extra-380'],limitations=['战时各方与控制边界资料仍不完整；本轮未虚构精确兵力及逐日占领线。']))

if __name__=='__main__':main()

