import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {capitalsAtYear,reviewedCapitals} from '../src/capitals.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {activePolities} from '../src/temporal.mjs';
import {selectFlag} from '../src/archive-rules.mjs';
import {leadershipFor} from '../src/archive-rules.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';

const read=name=>JSON.parse(readFileSync(new URL('../public/data/'+name,import.meta.url),'utf8'));
const index=read('map-capitals.json'),identities=read('curated-facts.json').identities;
const shardCache=new Map();
function world(year){
 const c=Math.floor(year/100);
 if(!shardCache.has(c))shardCache.set(c,read(`temporal/${c}.geojson`));
 return activePolities(shardCache.get(c),year);
}
const capitals=year=>capitalsAtYear(world(year),year,index,identities).features;
const labels=(year,name)=>capitals(year).filter(f=>f.properties.owner===name).map(f=>f.properties.label);

test('capital markers follow the selected year and archive identity',()=>{
 assert.deepEqual(labels(1400,'Ming Dynasty'),['应天府']);
 assert.deepEqual(labels(1444,'Ming Dynasty'),['北京']);
 assert.deepEqual(labels(1822,'Bourbon Kingdom of France'),['巴黎']);
 assert.deepEqual(labels(814,'Abbasid Caliphate'),['巴格达']);
 assert.deepEqual(labels(850,'Abbasid Caliphate'),['萨迈拉']);
 assert.ok(labels(100,'Roman Empire').includes('罗马'));
 const culture={type:'FeatureCollection',features:[{type:'Feature',properties:{NAME:'Sample',qid:'Q2277',representationKind:'archaeological-culture'},geometry:{type:'Polygon',coordinates:[]}}]};
 assert.equal(capitalsAtYear(culture,100,index,identities).features.length,0);
});

test('current map covers national capitals and can show multiple seats',()=>{
 const current=capitals(2024);
 assert.ok(new Set(current.map(f=>f.properties.owner)).size>=184);
 assert.deepEqual(labels(2024,'South Africa').sort(),['开普敦（立法首都）','布隆方丹（司法首都）','比勒陀利亚（行政首都）'].sort());
 assert.deepEqual(labels(2024,'Palau'),['恩吉鲁穆德']);
});

test('the 1822 white banner identifies the Bourbon Restoration and cites its history',()=>{
 const flags=read('flags.json').entities;
 const flag=selectFlag(flags.Q207162,1822).flag;
 assert.equal(flag.role,'波旁复辟白旗');
 assert.match(flag.periodNote,/百日王朝/);
 assert.match(flag.periodSource,/elysee/);
 assert.equal(selectFlag(flags.Q207162,1415).flag,undefined);
});


test('city labels and locations change with political control and documented capital moves',()=>{
 assert.deepEqual(labels(1444,'Ottoman Empire'),['埃迪尔内']);
 assert.deepEqual(labels(1500,'Ottoman Empire'),['伊斯坦布尔']);
 assert.deepEqual(reviewedCapitals(index,'Q12544',1444).map(row=>row[0]),['君士坦丁堡']);
 assert.deepEqual(reviewedCapitals(index,'Q12544',1220),[]);
 assert.deepEqual(reviewedCapitals(index,'Q178897',1220).map(row=>row[0]),['君士坦丁堡']);
 assert.deepEqual(reviewedCapitals(index,'Q181254',1220).map(row=>row[0]),['尼西亚']);
 assert.deepEqual(labels(1520,'Safavid Dynasty'),['大不里士']);
 assert.deepEqual(labels(1570,'Safavid Dynasty'),['加兹温']);
 assert.deepEqual(labels(1600,'Safavid Dynasty'),['伊斯法罕']);
 assert.deepEqual(labels(1916,'Russian Empire'),['彼得格勒']);
 assert.deepEqual(labels(100,'Nabataeans'),['佩特拉']);
});

test('stars stay in the displayed territory and retain the documented Durrani capital in the archive',()=>{
 assert.deepEqual(labels(1748,'Durrani Empire'),[]);
 assert.deepEqual(reviewedCapitals(index,'Q467627',1748).map(row=>row[0]),['坎大哈']);
 assert.deepEqual(labels(1752,'Durrani Empire'),['坎大哈']);
 assert.deepEqual(labels(1775,'Durrani Empire'),['喀布尔']);
 for(const year of [100,814,1444,1500,1748,1752,1775,1916,1950,2024]){
  const frame=world(year);
  for(const marker of capitalsAtYear(frame,year,index,identities).features){
   assert.ok(frame.features.some(f=>!f.properties.controlArea&&
    (f.properties.SUBJECTO?.trim()||f.properties.NAME)===marker.properties.owner&&
    pointInGeometry(marker.geometry.coordinates,f.geometry)),`${year} ${marker.properties.label}`);
  }
 }
});

test('British, French and Russian seats remain visible through renames and transfers',()=>{
 for(const [year,name,label] of [
  [1000,'Kingdom of England','温切斯特'],[1090,'Norman England','伦敦·威斯敏斯特'],
  [1200,'Angevin Empire','伦敦·威斯敏斯特（英格兰行政中心）'],
  [1444,'Kingdom of England','伦敦'],[1801,'United Kingdom of Great Britain and Ireland','伦敦'],
  [1000,'Kingdom of France','巴黎'],[1425,'Kingdom of France','布尔日'],[1444,'Kingdom of France','巴黎'],
  [1685,'Kingdom of France','凡尔赛'],[1715,'Kingdom of France','巴黎'],[1725,'Kingdom of France','凡尔赛'],
  [1789,'Kingdom of France','巴黎'],[1796,'French Directory','巴黎'],[1835,'Bourbon Kingdom of France','巴黎'],
  [1941,'Vichy France','维希'],[1945,'French Fourth Republic','巴黎'],
  [1685,'Tsardom of Russia','莫斯科'],[1725,'Russian Empire','圣彼得堡'],[1728,'Russian Empire','莫斯科'],
  [1732,'Russian Empire','圣彼得堡'],[1917,'Russian Republic','彼得格勒'],
  [1918,'Russian Socialist Federative Soviet Republic','莫斯科'],
  [1920,'Republics of the Soviet Union','莫斯科'],[1922,'Union of Soviet Socialist Republics','莫斯科'],
  [1850,'Empire of Brazil','里约热内卢'],[2024,'Republic of Brazil','巴西利亚'],
 ])assert.deepEqual(labels(year,name),[label],`${year} ${name}`);
 // The 1944 map has Paris in the German-controlled polygon. Keep the capital in the archive.
 assert.deepEqual(labels(1944,'France'),[]);
 assert.deepEqual(reviewedCapitals(index,'Q142',1944).map(row=>row[0]),['巴黎']);
});

test('new historical capital records match their active polities and contemporary names',()=>{
 for(const [year,name,label] of [
  [100,'Parthian Empire','泰西封'],[100,'Kingdom of Axum','阿克苏姆'],
  [1000,'Northern Song','东京·汴京'],[1000,'Liao Dynasty','上京临潢府'],
  [1000,'Heian Japan','平安京'],[1000,'Ghaznavid Empire','加兹尼'],
  [1200,'Southern Song','临安'],[1444,'Lê Dynasty','东京（升龙）'],
  [1444,'Vijayanagara Empire','毗奢耶那伽罗（亨比）'],
  [1500,'Kingdom of Kongo','姆班扎刚果'],[1500,'Kingdom of Scotland','爱丁堡'],
  [1603,'Iberian Union','巴利亚多利德'],[1700,'Kingdom of Spain','马德里'],
  [1850,'Qajar Dynasty','德黑兰'],
 ])assert.deepEqual(labels(year,name),[label],`${year} ${name}`);
 assert.deepEqual(labels(1000,'Buyid Dynasty').sort(),['巴格达（伊拉克）','雷伊（吉巴勒）','设拉子（法尔斯）'].sort());
 assert.deepEqual(reviewedCapitals(index,'Q80702',1700,'Spain Colony - Mexico').map(row=>row[0]),['墨西哥城（新西班牙首府）']);
 assert.deepEqual(reviewedCapitals(index,'Q80702',1700,'Spanish Empire').map(row=>row[0]),['马德里']);
 assert.deepEqual(reviewedCapitals(index,'Q129286',1910).map(row=>row[0]),['加尔各答']);
 assert.deepEqual(reviewedCapitals(index,'Q129286',1935).map(row=>row[0]),['新德里']);
});

test('the Austrian, Ottoman, Iberian and Brandenburg capital gaps have dated coverage',()=>{
 for(const [year,name,label] of [
  [1300,'Austrian Hereditary Lands','维也纳'],[1850,'Austrian Empire','维也纳'],
  [1900,'Austria-Hungary','维也纳'],[1900,'Austria-Hungary','布达佩斯（匈牙利政府所在地）'],
  [1366,'Ottoman Empire','布尔萨（旧都）'],[1375,'Ottoman Empire','埃迪尔内'],
  [1453,'Ottoman Empire','伊斯坦布尔'],[1700,'Ottoman Empire','伊斯坦布尔'],
  [1850,'Ottoman Empire','伊斯坦布尔'],[1900,'Ottoman Empire','伊斯坦布尔'],
  [1444,'Crown of Castile','巴利亚多利德（王廷驻地之一）'],
  [1850,'Kingdom of Spain','马德里'],[2021,'Kingdom of Spain','马德里'],
  [1933,'Second Spanish Republic','马德里'],[1937,'Second Spanish Republic','巴伦西亚'],
  [1300,'Margraviate of Brandenburg','哈弗尔河畔勃兰登堡（早期统治中心）'],
  [1500,'Electorate of Brandenburg','柏林—科隆城（施普雷河畔）'],
  [1620,'Brandenburg-Prussia','柏林—科隆城（选侯驻地）'],
 ]) assert.ok(labels(year,name).includes(label),`${year} ${name} ${label}`);
 assert.deepEqual(labels(1921,'Ottoman Empire'),[]);
 assert.deepEqual(reviewedCapitals(index,'Q12560',1921).map(row=>row[0]),['伊斯坦布尔']);
});

test('the 1706–1712 Polish succession faction is represented within the Commonwealth',()=>{
 for(const year of [1706,1709,1712]){
  const features=world(year).features;
  assert.ok(!features.some(f=>f.properties.NAME==='Pro-Swedish Poland'));
  const commonwealth=features.find(f=>f.properties.NAME==='Polish-Lithuanian Commonwealth');
  assert.ok(pointInGeometry([27.56,53.90],commonwealth.geometry));
  assert.match(commonwealth.properties.representationNote,/奥古斯特二世复位/);
 }
 const war=warsAtYear(read('conflicts.json'),read('war-details.json'),1709).find(w=>w.id==='historic-great-northern-war');
 assert.ok(warInvolvesPolity(war,'Polish-Lithuanian Commonwealth',1709));
 assert.deepEqual(participantsAt(war,1709).filter(p=>p.name.endsWith('faction')).map(p=>p.side).sort(),['1','2']);
});

test('Prussian, Nordic, Commonwealth and Irish seats follow the map identities',()=>{
 for(const [year,name,label] of [
  [1570,'Duchy of Prussia','柯尼斯堡'],[1740,'Kingdom of Prussia','柏林'],
  [1807,'Kingdom of Prussia','梅梅尔（临时王廷）'],[1820,'Kingdom of Prussia','柏林'],[1863,'Kingdom of Prussia','柏林'],
  [1000,'Kingdom of Denmark','罗斯基勒（王室中心）'],[1444,'Kingdom of Denmark','哥本哈根'],
  [1250,'Kingdom of Norway','卑尔根（王室驻地）'],[1300,'Kingdom of Norway','奥斯陆（王室驻地）'],
  [1850,'Kingdom of Norway','克里斯蒂安尼亚'],[1910,'Kingdom of Norway','克里斯蒂亚尼亚'],
  [2024,'Kingdom of Norway','奥斯陆'],[1620,'Swedish Empire','斯德哥尔摩（王室驻地）'],
  [1850,'Kingdom of Sweden','斯德哥尔摩'],
  [1590,'Polish-Lithuanian Commonwealth','克拉科夫'],[1709,'Polish-Lithuanian Commonwealth','华沙（王廷与政府驻地）'],
  [1000,'Gaelic Irish Kingdoms','卡舍尔（芒斯特王室据点）'],[1444,'Lordship of Ireland','都柏林'],
  [1444,'Gaelic Irish Lordships','邓甘嫩（蒂龙奥尼尔家族据点）'],[1570,'Kingdom of Ireland','都柏林'],
  [1590,'Mughal Empire','拉合尔'],[1650,'Mughal Empire','沙贾汗纳巴德（德里）'],
  [1790,'Konbaung Dynasty','阿马拉布拉'],[1871,'Konbaung Dynasty','曼德勒'],
 ])assert.ok(labels(year,name).includes(label),`${year} ${name} ${label}`);
 assert.deepEqual(reviewedCapitals(index,'Q27306',1808).map(row=>row[0]),['柯尼斯堡（临时王廷）']);
 assert.deepEqual(labels(1808,'Kingdom of Prussia'),[]);
 const berlin=capitals(1820).find(f=>f.properties.owner==='Kingdom of Prussia');
 assert.match(berlin.properties.federationLabel,/德意志邦联/);
});

test('an unresolved manual description does not mask another dated capital record',()=>{
 const frame={features:[{properties:{NAME:'Sample',qid:'Q1'},geometry:{type:'Polygon',coordinates:[[[0,0],[4,0],[4,4],[0,4],[0,0]]]}}]};
 const cityIndex={archive:{Q1:[['迁都沿革',null,100,120,null,true],['城名',[2,2],105,115,null,false]]},modern:{},hasDated:['Q1']};
 assert.deepEqual(capitalsAtYear(frame,110,cityIndex,{}).features.map(f=>f.properties.label),['城名']);
 assert.equal(capitalsAtYear(frame,119,cityIndex,{}).features.length,0);
});

test('Venice and the Baltic orders show their dated, distinct seats',()=>{
 assert.deepEqual(labels(1444,'Republic of Venice'),['威尼斯']);
 assert.deepEqual(labels(1504,'Republic of Venice'),['威尼斯']);
 assert.deepEqual(labels(1444,'Teutonic Order'),['马林堡']);
 assert.deepEqual(labels(1504,'Teutonic Order'),['柯尼斯堡']);
 assert.deepEqual(labels(1504,'Livonian Confederation').sort(),[
  '文登（骑士团团长驻地）','里加（大主教驻地）',
 ]);
});

test('American state and colonial seats appear on their own territories',()=>{
 for(const [year,name,label] of [
  [1490,'Aztec Triple Alliance','特诺奇提特兰'],[1490,'Michoacán','钦聪灿'],
  [1490,'Inca Empire','库斯科'],[1550,'Inca Empire','比尔卡班巴（新印加王廷）'],
  [1550,'Itza Mayans','诺赫佩滕（伊察王廷）'],
  [1550,'Spain Colony - Mexico','墨西哥城（新西班牙首府）'],
  [1650,'Spain Colony - Peru','利马（秘鲁总督区首府）'],
  [1650,'New France','魁北克'],[1650,'New Netherland','新阿姆斯特丹'],
  [1650,'New Sweden','克里斯蒂娜堡'],
  [1725,'Portugal Colony - Brazil','萨尔瓦多（巴西总督府驻地）'],
  [1800,'Portugal Colony - Brazil','里约热内卢（巴西行政中心）'],
  [1750,'Spain Colony - Cuba','哈瓦那'],[1750,'Spain Colony - Puerto Rico','圣胡安'],
  [1850,'United Kingdom Colony - Jamaica','西班牙镇'],
 ])assert.ok(labels(year,name).includes(label),`${year} ${name} ${label}`);
 assert.ok(!labels(1725,'Spain Colony - Mexico').includes('马德里'));
 assert.deepEqual(reviewedCapitals(index,'Q382593',1750,'New Netherland'),[]);
});

test('post-Angkor Cambodian records share one clickable territory and dated archive',()=>{
 const facts=read('polity-facts.json').entities;
 for(const year of [1700,1710,1725,1735,1750,1800,1850]){
  const frame=world(year),rows=frame.features.filter(f=>['Cambodia','Khmer Empire','Kingdom of Cambodia'].includes(f.properties.NAME));
  assert.equal(rows.length,1,`${year} duplicate Cambodian polity`);
  assert.equal(rows[0].properties.qid,'Q4919413');
  assert.deepEqual(labels(year,'Kingdom of Cambodia'),['乌栋']);
  assert.ok(leadershipFor(facts.Q4919413,undefined,year).rows.length,`${year} missing ruler`);
 }
 const original=shardCache.get(17).features.filter(f=>['Cambodia','Khmer Empire'].includes(f.properties.NAME)&&f.properties.validFrom<=1725&&f.properties.validTo>=1725);
 const merged=world(1725).features.find(f=>f.properties.NAME==='Kingdom of Cambodia');
 for(const point of [[104.7425,11.8239],[107,12]]){
  assert.ok(original.some(f=>pointInGeometry(point,f.geometry)));
  assert.ok(pointInGeometry(point,merged.geometry));
 }
 assert.ok(leadershipFor(facts.Q4919413,undefined,1725).rows.some(r=>r.label==='萨达二世'));
 assert.ok(world(1400).features.some(f=>f.properties.NAME==='Khmer Empire'));
});

test('Pakistan and Laos retain capital markers across the former modern cutoff',()=>{
 for(const [year,name,label] of [
  [1950,'Islamic Republic of Pakistan','卡拉奇'],
  [1965,'Islamic Republic of Pakistan','拉瓦尔品第（临时首都）'],
  [1971,'Islamic Republic of Pakistan','伊斯兰堡'],
  [2023,'Islamic Republic of Pakistan','伊斯兰堡'],
  [1960,'Kingdom of Laos','万象（行政首都）'],
  [1971,'Kingdom of Laos','万象（行政首都）'],
  [1971,'Kingdom of Laos','琅勃拉邦（王室驻地）'],
  [2023,'Communist Laos','万象'],
 ])assert.ok(labels(year,name).includes(label),`${year} ${name} ${label}`);
});

test('reviewed untranslated capitals are Chinese in the index and archives',()=>{
 const entities=read('polity-facts.json').entities;
 for(const year of [1351,1739]){
  const found=capitals(year).filter(f=>['Sultanate of Sulu','Jaffna kingdom','Rasulid Dynasty'].includes(f.properties.owner));
  assert.ok(found.length);
  for(const f of found)assert.match(f.properties.label,/[\u3400-\u9fff]/u);
 }
 for(const entity of Object.values(entities))for(const row of entity.fields.capital||[]){
  assert.ok(!['Maimbung','Jolo','Buansa','Nallur','Old City of Taiz'].includes(row.label));
 }
 const flag=selectFlag(read('flags.json').entities.Q627449,1725);
 assert.equal(flag.reference,false);
 assert.match(flag.flag.role,/汉达基黑旗/);
 assert.ok(flag.flag.periodSource);
 assert.equal(selectFlag(read('flags.json').entities.Q627449,1800).flag,undefined);
});
