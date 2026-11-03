import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {scopedFacts} from '../src/archive-rules.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {regionsAtYear} from '../src/regions.mjs';
import {cowCode} from '../src/country-codes.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../public/data/'+n,import.meta.url),'utf8'));
const cache=new Map(),world=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`temporal/${c}.geojson`));return activePolities(cache.get(c),y);};
const owners=(y,p)=>world(y).features.filter(f=>pointInGeometry(p,f.geometry));
const facts=read('polity-facts.json').entities,curated=read('curated-facts.json');
const db=read('conflicts.json'),details=read('war-details.json');
const id=f=>curated.identities[f.properties.NAME]||f.properties.qid;

test('Hungary covers its 1949 handover and 1956–57 is never Austria-Hungary',()=>{
 for(const y of [1949,1956,1957]){
  for(const p of [[19.04,47.5],[21.6,47.53]])assert.deepEqual(owners(y,p).map(f=>f.properties.NAME),["Hungarian People's Republic"]);
  assert.deepEqual(owners(y,[16.37,48.21]).map(f=>f.properties.NAME),['Second Republic of Austria']);
  assert.ok(!world(y).features.some(f=>f.properties.qid==='Q28513'||f.properties.displayName==='奥匈帝国'));
 }
 const pm=scopedFacts(facts.Q16410,'headOfGovernment',1956).rows;
 assert.ok(pm.some(r=>r.value==='Q177917'));assert.ok(pm.some(r=>r.value==='Q200850'));
 assert.equal(cowCode("Hungarian People's Republic",undefined,{},1956),'310');
 assert.equal(cowCode("Hungarian People's Republic",undefined,{},1918),undefined);
 assert.ok(warsAtYear(db,details,1956).some(w=>warInvolvesPolity(w,"Hungarian People's Republic",1956)));
});

test('Hainan has one PRC owner in every newly reported missing year',()=>{
 for(const y of [1950,1951,1952,1953])for(const p of [[110.3,20],[109.5,18.3],[109.6,19.2]])assert.deepEqual(owners(y,p).map(f=>f.properties.NAME),["People's Republic of China"]);
 assert.deepEqual(owners(1949,[109.6,19.2]).map(f=>f.properties.NAME),['Republic of China']);
});

test('Gulf sheikhdoms are separate and British labels end at independence',()=>{
 for(const [p,n]of [[[55.3,25.2],'Sheikhdom of Dubai'],[[54.5,24.2],'Sheikhdom of Abu Dhabi'],[[56.3,25.1],'Sheikhdom of Fujairah']])assert.deepEqual(owners(1950,p).map(f=>f.properties.NAME),[n]);
 for(const y of [1972,1980,2000,2024]){
  for(const [p,n]of [[[55.3,25.2],'United Arab Emirates'],[[54.5,24.2],'United Arab Emirates'],[[50.58,26.22],y<2002?'State of Bahrain':'Kingdom of Bahrain']])assert.deepEqual(owners(y,p).map(f=>f.properties.NAME),[n]);
  const kw=owners(y,[47.98,29.38]);assert.equal(kw.length,1);assert.equal(kw[0].properties.qid,'Q817');assert.ok(['Kuwait','State of Kuwait'].includes(kw[0].properties.NAME));
  assert.ok(!world(y).features.some(f=>/^United Kingdom Colony - (Bahrain|Kuwait|United Arab Emirates|Iraq|Jordan|Yemen|Saudi Arabia|Qatar|Oman)$/.test(f.properties.NAME)));
 }
 for(const y of [1800,1840,1870,1900]){
  const muscat=owners(y,[58.4,23.6]);assert.equal(muscat.length,1);assert.equal(muscat[0].properties.NAME,'Sultanate of Muscat and Oman');
  assert.ok(!world(y).features.some(f=>f.properties.NAME==='Omani Al Busaidi State'));
 }
 const yem=world(1840).features.find(f=>f.properties.NAME==='Imamate of Yemen');assert.equal(yem.properties.displayName,'也门伊玛目国');assert.ok(id(yem).startsWith('local:'));
 assert.ok(!world(1840).features.some(f=>/列表|停战诸国/.test(f.properties.displayName)));
});

test('CCP and nationalist sides retain separate dated identities in merged civil-war records',()=>{
 for(const y of [1946,1948,1949,1950]){
  const w=warsAtYear(db,details,y).find(w=>w.id==='cow-intra-723.5'||w.also?.some(s=>s.id==='cow-intra-723.5'));
  assert.ok(w);assert.ok(warInvolvesPolity(w,'Communist Party of China',y));assert.ok(warInvolvesPolity(w,'Republic of China',y));
  const ps=participantsAt(w,y);assert.equal(ps.find(p=>p.displayName==='国民政府与国民党军').side,'1');assert.equal(ps.find(p=>p.displayName==='中国共产党及人民解放军').side,'2');
  if(y>=1949)assert.ok(warInvolvesPolity(w,"People's Republic of China",y));
 }
});

test('Ottoman-Persian wars and contemporary rulers link through corrected polity names',()=>{
 for(const[y,n]of [[1540,'Safavid Dynasty'],[1585,'Safavid Dynasty'],[1605,'Safavid Dynasty'],[1628,'Safavid Dynasty'],[1745,'Afsharid Iran'],[1776,'Zand Dynasty'],[1823,'Qajar Dynasty']]){
  const ws=warsAtYear(db,details,y).filter(w=>w.id.startsWith('historic-ottoman-'));
  assert.ok(ws.some(w=>warInvolvesPolity(w,'Ottoman Empire',y)&&warInvolvesPolity(w,n,y)),`${y} ${n}`);
  const f=world(y).features.find(f=>f.properties.NAME===n);assert.ok(f,n);assert.ok(scopedFacts(facts[id(f)],'ruler',y).rows.length,`${y} ${id(f)}`);
 }
 const w=warsAtYear(db,details,1821).filter(w=>w.id==='cow-extra-309'||w.id==='historic-ottoman-qajar-1821');assert.equal(w.length,1);
});

test('Southern Shaanxi has sourced annual control and late-Ming wars',()=>{
 for(const[y,p,n]of [[1645,[107,33.1],'Southern Shaanxi Anti-Qing Forces'],[1646,[107,33.1],'Qing Dynasty'],[1646,[109,32.7],'Southern Shaanxi Anti-Qing Forces'],[1647,[107,33.1],'Qing Dynasty'],[1647,[109,32.7],'Qing Dynasty']])assert.deepEqual(owners(y,p).map(f=>f.properties.NAME),[n]);
 for(const[y,n]of [[1635,'Ming Dynasty'],[1645,'Southern Ming'],[1646,'Southern Shaanxi Anti-Qing Forces']])assert.ok(warsAtYear(db,details,y).some(w=>warInvolvesPolity(w,n,y)));
});

test('Late Kievan Rus overlay gives way to principalities and an explicit unseparated region',()=>{
 for(const y of [1150,1200,1230]){
  assert.ok(!world(y).features.some(f=>f.properties.NAME==="Kievan Rus'"));
  assert.deepEqual(owners(y,[30.5,50.45]).map(f=>f.properties.NAME),['Principality of Kiev']);
  assert.ok(!world(y).features.some(f=>/列表/.test(f.properties.displayName)));
 }
 assert.deepEqual(scopedFacts(facts['local:rus-unseparated'],'ruler',1200).rows,[]);
});

test('Qin partition countries no longer share a catalogue or war identity',()=>{
 const fs=world(-206).features;
 const expected=['西楚','汉国','雍国','塞国','翟国','常山国','代国','济北国','胶东国','九江国','河南国','殷国','韩国','临江国','辽东国','西魏国','齐国','燕国'];
 for(const n of expected){const f=fs.find(f=>f.properties.displayName===n);assert.ok(f,n);assert.ok(id(f).startsWith('local:qin-successor-'));assert.ok(scopedFacts(facts[id(f)],'ruler',-206).rows.length,n);}
 assert.equal(new Set(fs.filter(f=>expected.includes(f.properties.displayName)).map(id)).size,expected.length);
 assert.ok(!fs.some(f=>/项羽十八诸侯|楚汉战争/.test(f.properties.displayName)||['Q5349053','Q1151705'].includes(f.properties.qid)));
 assert.ok(!world(-205).features.some(f=>['Sai Kingdom','Zhai Kingdom','Jiaodong Kingdom','Jibei Kingdom'].includes(f.properties.NAME)));
 assert.ok(!world(-207).features.some(f=>['Western Chu','Zhai Kingdom'].includes(f.properties.NAME)));
 const war=warsAtYear(db,details,-205).find(w=>w.id==='historic-chu-han');assert.ok(warInvolvesPolity(war,'Han Kingdom (Liu Bang)',-205));assert.ok(warInvolvesPolity(war,'Western Chu',-205));
});

test('Xin dynasty has its correct dates, internal land coverage and successor states',()=>{
 for(const y of [6,8]){assert.ok(!world(y).features.some(f=>f.properties.NAME==='Xin Dynasty'));assert.deepEqual(owners(y,[108.9,34.2]).map(f=>f.properties.NAME),['Han Dynasty']);}
 for(let y=9;y<=22;y++)for(const p of [[108.9,34.2],[112.5,33],[104.1,30.6],[113.3,23.1],[112.4,34.6]])assert.deepEqual(owners(y,p).map(f=>f.properties.NAME),['Xin Dynasty']);
 for(const y of [23,24,25,29,30])assert.ok(!world(y).features.some(f=>f.properties.NAME==='Xin Dynasty'));
 assert.deepEqual(owners(24,[108.9,34.2]).map(f=>f.properties.NAME),['Gengshi Han']);
 assert.deepEqual(owners(25,[112.4,34.6]).map(f=>f.properties.NAME),['Han Dynasty']);
 assert.deepEqual(owners(25,[104.1,30.6]).map(f=>f.properties.NAME),['Chengjia']);
 assert.deepEqual(owners(25,[108.9,34.2]).map(f=>f.properties.NAME),['Chimei Han']);
 assert.ok(warsAtYear(db,details,25).some(w=>warInvolvesPolity(w,'Chengjia',25)));
});

test('Guangxi, Hainan and Ottoman provinces change names with their own eras',()=>{
 const modern=read('provinces.geojson'),historic=read('historical-provinces.geojson');
 const at=(y,xy)=>regionsAtYear(modern,historic,world(y),y).features.filter(f=>pointInGeometry(xy,f.geometry));
 assert.ok(at(1820,[108.3,23.1]).some(f=>f.properties.label==='广西省'));
 assert.ok(!at(1820,[108.3,23.1]).some(f=>/壮族|僮族/.test(f.properties.label)));
 assert.ok(at(1955,[108.3,23.1]).some(f=>f.properties.label==='广西省'));
 assert.ok(at(1960,[108.3,23.1]).some(f=>f.properties.label==='广西僮族自治区'));
 assert.ok(at(1951,[109.6,19.2]).some(f=>f.properties.label==='海南行政区（广东省）'));
 assert.ok(at(1800,[32.8,39.9]).some(f=>f.properties.label==='安纳托利亚行省'));
 assert.ok(at(1900,[32.8,39.9]).some(f=>f.properties.label==='安卡拉州'));
});
