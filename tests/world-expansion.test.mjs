import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {scopedFacts} from '../src/archive-rules.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {regionsAtYear} from '../src/regions.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {colorIdentity} from '../src/color-identity.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url),'utf8'));
const facts=read('polity-facts.json').entities,cur=read('curated-facts.json'),wars=read('conflicts.json'),details=read('war-details.json');
const modern=read('provinces.geojson'),historic=read('historical-provinces.geojson');
const cache=new Map(),world=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`temporal/${c}.geojson`));return activePolities(cache.get(c),y);};
const rulers=(q,y)=>scopedFacts(facts[q],'ruler',y).rows;
const regions=y=>regionsAtYear(modern,historic,{type:'FeatureCollection',features:[]},y);
const at=(db,c,p)=>db.features.filter(f=>f.properties.country===c&&pointInGeometry(p,f.geometry));

test('global expansion supplies named monarchs and presidents across the actual missing periods',()=>{
 for(const[q,y,label]of [['Q179876',1000,'埃塞尔雷德'],['Q70972',1200,'腓力二世'],['Q45670',1900,'卡洛斯一世'],['Q1062422',1825,'巴基道'],['Q878309',1100,'李仁宗'],['Q3111454',1285,'陈仁宗'],['Q722071',1850,'夸库·杜阿'],['Q207521',1700,'伊亚苏一世'],['Q1028',1900,'阿齐兹'],['Q217230',1860,'佩德罗二世'],['Q155',1900,'萨莱斯'],['Q298',1900,'埃绍伦'],['Q414',1900,'罗卡']])assert.ok(rulers(q,y).some(r=>r.label.includes(label)),`${q} ${y} ${label}`);
 // 1883 has four successive Nguyen emperors, not a single reign invented to fill it.
 const names=rulers('Q6500483',1883).map(r=>r.label).join(' ');
 for(const n of ['嗣德帝','育德帝','协和帝','建福帝'])assert.ok(names.includes(n));
 assert.ok(rulers('Q207521',1938).some(r=>/流亡/.test(r.roleLabel)));
 assert.ok(!rulers('Q45670',1384).some(r=>r.supplement==='world-rosters-2026-11-02'));
});

test('new dated appointments have exact human identifiers, sources, and bounded terms',()=>{
 const r=read('world-rosters-review.json');assert.ok(r.summary.added>=200);assert.ok(r.summary.people>=190);
 for(const x of r.appointments){assert.match(x.value,/^Q\d+$/);assert.ok(x.from<=x.to);assert.ok(x.citation.some(s=>s.startsWith('https://www.wikidata.org/wiki/')));assert.ok(x.citation.length>=2);}
});

test('period-specific identities expose Burmese kings and Argentine presidents on the map',()=>{
 const f=world(1825).features.find(f=>f.properties.NAME==='Konbaung Dynasty');assert.ok(f);assert.equal(f.properties.qid,'Q1062422');assert.ok(!world(1825).features.some(f=>f.properties.NAME==='Burma'));
 const a=world(1900).features.find(f=>f.properties.NAME==='Argentine Republic');assert.ok(a);assert.equal(cur.identities[a.properties.NAME]||a.properties.qid,'Q414');assert.ok(!world(1900).features.some(f=>f.properties.NAME==='Argentine Confederation'));
 assert.ok(world(1850).features.some(f=>f.properties.NAME==='Argentine Confederation'));
 assert.equal(colorIdentity('Burma'),colorIdentity('Konbaung Dynasty'));assert.equal(colorIdentity('Argentine Confederation'),colorIdentity('Argentine Republic'));
});

test('new and enriched wars appear in the corresponding countries and correct entry years',()=>{
 for(const[y,slug,names]of [[1216,'historic-barons-first',['Kingdom of England']],[1297,'historic-scottish-independence-first',['Kingdom of England','Kingdom of Scotland']],[1645,'historic-portuguese-restoration',['Kingdom of Portugal','Kingdom of Spain']],[1076,'historic-ly-song',['Ly Dynasty','Northern Song']],[1285,'historic-yuan-viet-1285',['Tran Dynasty','Yuan Dynasty']],[1767,'historic-qing-burma',['Konbaung Dynasty','Qing Dynasty']],[1665,'historic-mbwila',['Kingdom of Kongo','Kingdom of Portugal']],[1823,'historic-brazilian-independence',['Empire of Brazil','Kingdom of Portugal']],[1874,'cow-extra-367',['Ashanti Empire']],[1868,'cow-extra-362',['Ethiopian Empire']],[1852,'cow-extra-339',['Konbaung Dynasty']]]){
  const w=warsAtYear(wars,details,y).find(w=>w.id===slug||w.also?.some(x=>x.id===slug));assert.ok(w,slug);for(const n of names)assert.ok(warInvolvesPolity(w,n,y),`${slug}: ${n}`);
 }
 const war=y=>warsAtYear(wars,details,y).find(w=>w.id==='historic-thirty-years');
 assert.ok(!warInvolvesPolity(war(1634),'Kingdom of France',1634));assert.ok(warInvolvesPolity(war(1635),'Kingdom of France',1635));
 assert.ok(warInvolvesPolity(war(1629),'Kingdom of Denmark',1629));assert.ok(!warInvolvesPolity(war(1630),'Kingdom of Denmark',1630));
 assert.equal(wars.wars.find(w=>w.id==='cow-extra-310').from,1823);
 for(const id of read('world-wars-review.json').enriched){const d=details.wars.find(d=>d.id===id);assert.ok(d.cause&&d.result&&d.sources.length);}
});

test('France actually merges regional shapes in 2016, with correct earlier name changes',()=>{
 const a=regions(2014),b=regions(2015),c=regions(2016);
 assert.equal(at(a,'France',[1.9,47.9])[0].properties.label,'中央大区');assert.equal(at(b,'France',[1.9,47.9])[0].properties.label,'中央-卢瓦尔河谷大区');
 assert.equal(at(b,'France',[.1,49.5])[0].properties.label,'上诺曼底大区');assert.equal(at(b,'France',[-.4,49.2])[0].properties.label,'下诺曼底大区');
 const upper=at(c,'France',[.1,49.5]),lower=at(c,'France',[-.4,49.2]);assert.equal(upper.length,1);assert.equal(lower.length,1);assert.equal(upper[0].properties.id,lower[0].properties.id);assert.equal(upper[0].properties.label,'诺曼底大区');
 assert.equal(at(c,'France',[-.58,44.84])[0].properties.id,at(c,'France',[.34,46.58])[0].properties.id);
 assert.equal(c.features.filter(f=>f.properties.country==='France'&&f.properties.supplement==='world-regions-2026-11-02').length,13);
});

test('Indian new states change the partition rather than only changing a modern label',()=>{
 const before=regions(1999),after=regions(2000);
 const patna=[85.1,25.6],ranchi=[85.3,23.3];assert.equal(at(before,'India',patna)[0].properties.id,at(before,'India',ranchi)[0].properties.id);assert.notEqual(at(after,'India',patna)[0].properties.id,at(after,'India',ranchi)[0].properties.id);
 assert.equal(at(after,'India',[78,30.3])[0].properties.label,'北安查尔邦');assert.equal(at(regions(2007),'India',[78,30.3])[0].properties.label,'北阿坎德邦');
 assert.equal(at(regions(2013),'India',[78.48,17.38])[0].properties.label,'安得拉邦');assert.equal(at(regions(2014),'India',[78.48,17.38])[0].properties.label,'特伦甘纳邦');
 assert.match(at(regions(2018),'India',[77.58,34.15])[0].properties.label,/查谟和克什米尔邦/);assert.equal(at(regions(2019),'India',[77.58,34.15])[0].properties.label,'拉达克中央直辖区');
});

test('Brazilian province/state names and mergers have no overlapping old locator labels',()=>{
 const a=regions(1978),b=regions(1979),p=[-54.6,-20.5],q=[-56.1,-15.6];assert.equal(at(a,'Brazil',p)[0].properties.id,at(a,'Brazil',q)[0].properties.id);assert.notEqual(at(b,'Brazil',p)[0].properties.id,at(b,'Brazil',q)[0].properties.id);
 assert.equal(at(regions(1960),'Brazil',[-60.67,2.82])[0].properties.label,'里奥布朗库联邦领地');assert.equal(at(regions(1962),'Brazil',[-60.67,2.82])[0].properties.label,'罗赖马联邦领地');
 const sp=at(regions(1840),'Brazil',[-46.63,-23.55]);assert.equal(sp.length,1);assert.equal(sp[0].properties.label,'圣保罗省');assert.equal(sp[0].properties.boundaryVisible,false);
 const curitiba=at(regions(1854),'Brazil',[-49.27,-25.43]);assert.equal(curitiba.length,1);assert.equal(curitiba[0].properties.label,'巴拉那省');
});

test('historical Asian names retain uncertainty and never assert modern locator outlines as exact old borders',()=>{
 const fs=historic.features.filter(f=>f.properties.supplement==='world-regions-2026-11-02'&&['Vietnam','Myanmar'].includes(f.properties.country));
 assert.ok(fs.length>=20);for(const f of fs){assert.equal(f.properties.geographicReference,true);assert.equal(f.properties.boundaryVisible,false);assert.ok(f.properties.sourceUrl.startsWith('https://'));}
 const d=regionsAtYear(modern,historic,world(1850),1850);const saigon=at(d,'Vietnam',[106.7,10.78]);assert.equal(saigon.length,1);assert.equal(saigon[0].properties.label,'嘉定省');
 const s=scopedFacts(facts.Q6500483,'government',1900).rows;assert.ok(s.some(r=>/法国保护/.test(r.label)));
});
