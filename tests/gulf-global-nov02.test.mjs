import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {mapName} from '../src/map-names.mjs';
import {baseColor} from '../src/colors.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {scopedFacts} from '../src/archive-rules.mjs';
import {dependenciesAt} from '../src/relationships.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
import {regionsAtYear} from '../src/regions.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url),'utf8'));
const cache=new Map(),world=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`temporal/${c}.geojson`));return activePolities(cache.get(c),y);};
const owners=(y,xy)=>world(y).features.filter(f=>pointInGeometry(xy,f.geometry));
const facts=read('polity-facts.json').entities,curated=read('curated-facts.json');

test('German monarchy headings retain their country name and imperial style',()=>{
 for(const y of [1871,1888,1900,1914,1918]){
  const p=world(y).features.find(f=>f.properties.NAME==='German Empire')?.properties;
  assert.ok(p,`${y} empire`);assert.equal(p.displayName,'德意志帝国');assert.equal(mapName(p),'德意志帝国');
 }
 assert.equal(mapName({NAME:'Kingdom of Germany',displayName:'德国'}),'德意志王国');
 assert.equal(mapName({NAME:'Weimar Republic',displayName:'德国'}),'德国');
 assert.equal(mapName({NAME:'Federal Republic of Germany',displayName:'西德'}),'西德');
});

test('1947–1955 Qatar is on its peninsula and Oman has its own governments',()=>{
 for(let y=1947;y<=1955;y++){
  for(const[xy,n]of [[[51.53,25.29],'Qatar Protectorate'],[[58.4,23.6],'Sultanate of Muscat and Oman'],[[57.53,22.93],'Imamate of Oman'],[[54.1,17.04],'Sultanate of Muscat and Oman']])assert.deepEqual(owners(y,xy).map(f=>f.properties.NAME),[n],`${y} ${xy}`);
  const q=owners(y,[51.53,25.29])[0].properties;
  assert.equal(q.qid,'local:qatar-protectorate');assert.equal(q.displayName,'卡塔尔');
  assert.ok(!world(y).features.some(f=>f.properties.qid==='Q944391'||f.properties.displayName==='卡塔尔历史'));
  const rel=dependenciesAt(world(y),[],y,curated.relations).filter(r=>r.child==='Qatar Protectorate');
  assert.equal(rel.length,1);assert.equal(rel[0].kind,'protectorate');assert.match(rel[0].parent,/United Kingdom/);
 }
 for(const y of [1972,1980,2000,2024]){
  assert.deepEqual(owners(y,[51.53,25.29]).map(f=>f.properties.NAME),['State of Qatar']);
  assert.deepEqual(owners(y,[58.4,23.6]).map(f=>f.properties.NAME),['Sultanate of Oman']);
 }
 assert.match(scopedFacts(facts['local:qatar-protectorate'],'ruler',1950).rows.map(r=>r.label).join(''),/阿里/);
 assert.match(scopedFacts(facts['local:oman-imamate-1913'],'ruler',1950).rows[0].label,/哈利利/);
 assert.notEqual(scopedFacts(facts['local:oman-imamate-1913'],'ruler',1950).rows[0].value,'Q111696671');
 assert.equal(baseColor('Qatar Protectorate'),baseColor('State of Qatar'));
 assert.equal(baseColor('Sultanate of Muscat and Oman'),baseColor('Sultanate of Oman'));
 assert.notEqual(baseColor('Imamate of Oman'),baseColor('Sultanate of Muscat and Oman'));
});

test('Korean dated monarchs cover every year while restoration terms stay separate',()=>{
 for(const[q,a,b]of [['Q28208',918,1392],['Q28179',1392,1897]])for(let y=a;y<=b;y++)assert.ok(scopedFacts(facts[q],'ruler',y).rows.length,`${q} ${y}`);
 assert.ok(scopedFacts(facts.Q28208,'ruler',1298).rows.some(r=>r.label==='高丽忠宣王'));
 assert.ok(!scopedFacts(facts.Q28208,'ruler',1300).rows.some(r=>r.label==='高丽忠宣王'));
 assert.ok(scopedFacts(facts.Q28208,'ruler',1310).rows.some(r=>r.label==='高丽忠宣王'));
 for(const[q,y,label]of [['Q156418',1892,'利留卡拉尼'],['Q1071439',1850,'腊纳瓦洛娜一世'],['Q202687',1500,'阿斯基亚·穆罕默德一世'],['Q1115291',1770,'郑信'],['Q1155700',1860,'拉玛四世']])assert.ok(scopedFacts(facts[q],'ruler',y).rows.some(r=>r.label.includes(label)),`${q} ${y}`);
 const portraits=read('portraits.json').people;
 for(const[q,y]of [['Q156418',1892],['Q1071439',1850],['Q28179',1444]]){
  const rs=scopedFacts(facts[q],'ruler',y).rows;
  assert.ok(rs.some(r=>portraits[r.value]&&existsSync(new URL('../public'+portraits[r.value].path,import.meta.url))));
 }
});

test('reviewed wars link to countries in active years and preserve pauses',()=>{
 const db=read('conflicts.json'),details=read('war-details.json');
 for(const[y,id,names]of [[1018,'historic-goryeo-khitan',['Goryeo','Liao Dynasty']],[1592,'historic-imjin',['Joseon','Ming Dynasty','Japanese clan - Toyotomi']],[1627,'historic-later-jin-joseon',['Joseon']],[1637,'historic-qing-joseon',['Joseon','Qing Dynasty']],[1766,'historic-burma-siam-1765',['Konbaung Dynasty','Ayutthaya Kingdom']],[1785,'historic-burma-siam-1785',['Konbaung Dynasty','Rattanakosin Kingdom']],[1803,'historic-haitian-revolution',['First French Empire']],[1845,'historic-nz-northern',['United Kingdom Colony - New Zealand']],[1954,'historic-jebel-akhdar',['Sultanate of Muscat and Oman','Imamate of Oman']]]){
  const w=warsAtYear(db,details,y).find(w=>w.id===id);assert.ok(w,id);
  for(const name of names)assert.ok(warInvolvesPolity(w,name,y),`${id} ${name}`);
  assert.ok(w.detail.cause&&w.detail.result&&w.detail.sources.length);
 }
 for(const y of [994,1009,1012,1017])assert.ok(!warsAtYear(db,details,y).some(w=>w.id==='historic-goryeo-khitan'));
 assert.ok(!warsAtYear(db,details,1956).some(w=>w.id==='historic-jebel-akhdar'));
 const oman=warsAtYear(db,details,1957).filter(w=>w.id==='historic-jebel-akhdar'||w.id==='ucdp-258');assert.equal(oman.length,1);
 assert.ok(warInvolvesPolity(oman[0],'Imamate of Oman',1957));
 const parties=participantsAt(oman[0],1957);assert.equal(parties.length,3);
 assert.equal(parties.find(p=>p.name==='Government of Oman').side,'1');
 assert.equal(parties.find(p=>p.name==='Government of United Kingdom').side,'1');
 assert.equal(parties.find(p=>p.name==='State of Oman/Free Oman').side,'2');
 const h=y=>warsAtYear(db,details,y).find(w=>w.id==='historic-haitian-revolution');
 assert.ok(participantsAt(h(1797),1797).some(p=>p.side==='1'&&p.polityNames?.includes('French First Republic')));
 assert.ok(!participantsAt(h(1797),1797).some(p=>p.side==='2'&&p.polityNames?.includes('French First Republic')));
});

test('province names and merged locating areas change across reforms',()=>{
 const modern=read('provinces.geojson'),historical=read('historical-provinces.geojson');
 const frame=y=>regionsAtYear(modern,historical,world(y),y).features;
 const at=(y,xy)=>frame(y).filter(f=>pointInGeometry(xy,f.geometry));
 assert.deepEqual(at(1444,[127.5,36.7]).map(f=>f.properties.label),['忠清道']);
 assert.ok(at(1900,[127.5,36.7]).some(f=>f.properties.label==='忠清北道'));
 assert.ok(!at(1900,[127.5,36.7]).some(f=>f.properties.label==='忠清道'));
 assert.ok(at(1895,[127.5,36.7]).some(f=>/旧域/.test(f.properties.label)));
 for(const[y,label]of [[1855,'新普利茅斯省'],[1860,'塔拉纳基省']])assert.ok(at(y,[174.2,-39.3]).some(f=>f.properties.label===label));
 assert.ok(!frame(1877).some(f=>f.properties.supplement==='dated-regions-2026-11-02'&&f.properties.country==='New Zealand'));
 for(const f of historical.features.filter(f=>f.properties.supplement==='dated-regions-2026-11-02')){
  assert.equal(f.properties.boundaryVisible,false);assert.equal(f.properties.geographicReference,true);
 }
});
