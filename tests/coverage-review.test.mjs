import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry,colorForName} from '../src/history.mjs';
import {scopedFacts} from '../src/archive-rules.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const cache=new Map();const world=y=>{let c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`public/data/temporal/${c}.geojson`));return activePolities(cache.get(c),y);};
const owners=(y,p)=>world(y).features.filter(f=>pointInGeometry(p,f.geometry));
test('Indian gaps contain dated rulers or explicitly distinct regional polities, not an early modern Indian nation',()=>{
 for(const[y,p,n]of [[1500,[72.58,23.02],'Gujarat Sultanate'],[1500,[77.41,23.26],'Malwa Sultanate'],[1750,[76.27,9.93],'Netherlands Colony - India'],[1750,[78.49,17.39],'Hyderabad State'],[1857,[80.95,26.85],'Awadh Rebel Government'],[1900,[72.88,19.08],'British Raj']])assert.ok(owners(y,p).some(f=>f.properties.NAME===n),`${y} ${n}`);
 assert.ok(owners(1600,[80.27,13.08]).length);assert.ok(!world(1750).features.some(f=>f.properties.NAME==='Republic of India'));
});
test('North Caucasus communities, the imamate and later Russian forts have dated coverage',()=>{
 for(const[y,p,n]of [[1750,[45.69,43.32],'North Caucasian Mountain Communities'],[1850,[47.5,42.98],'Russian Empire'],[1900,[41.02,43],'Russian Empire']])assert.ok(owners(y,p).some(f=>f.properties.NAME===n),`${y} ${n}`);
 const f=world(1850).features.find(f=>f.properties.NAME==='Caucasian Imamate');assert.ok(f);assert.ok(!world(1900).features.some(f=>f.properties.NAME==='Caucasian Imamate'));
});
test('Arabian oasis and state phases are explicit; Riyadh is not already Diriyah in 1750',()=>{
 assert.ok(owners(1750,[46.72,24.69]).some(f=>f.properties.NAME==='Riyadh Emirate of Dahham'));assert.ok(!owners(1750,[46.72,24.69]).some(f=>f.properties.NAME==='Emirate of Diriyah'));
 assert.ok(owners(1750,[57.53,22.93]).length);assert.ok(owners(1750,[45.03,12.79]).length);
 for(const y of [1900,1902,1915,1923,1932])assert.ok(!world(y).features.some(f=>f.properties.NAME==='Emirate of Nejd'),y);
 assert.ok(world(1902).features.some(f=>f.properties.NAME==='Emirate of Riyadh'));assert.ok(world(1923).features.some(f=>f.properties.NAME==='Sultanate of Nejd'));assert.ok(world(1932).features.some(f=>f.properties.NAME==='Saudi Arabia'));
 assert.equal(colorForName('Sultanate of Nejd'),colorForName('Emirate of Nejd'));
});
test('prehistoric snapshots expose typed evidence and do not project modern ethnonyms into 8000 BCE',()=>{
 const data=read('public/data/world_bc8000.geojson');assert.ok(data.features.filter(f=>f.properties.NAME?.trim()).every(f=>f.properties.representationKind&&f.properties.qid));assert.ok(!data.features.some(f=>['Bantu','Austronesians','Thai'].includes(f.properties.NAME)));
 const archaic=read('public/data/world_bc123000.geojson');assert.ok(archaic.features.some(f=>f.properties.representationKind==='human-presence'));
 const early=world(-3000).features;assert.ok(early.some(f=>f.properties.regionalCollection));assert.ok(early.some(f=>f.properties.representationKind==='archaeological-culture'));
});
test('culture records explain unrecorded rulers while real dynasties gain verified named people',()=>{
 const facts=read('public/data/polity-facts.json').entities;
 assert.ok(scopedFacts(facts['local:riyadh-dahham'],'ruler',1750).rows.some(r=>r.label==='达哈姆·本·达瓦斯'));
 assert.ok(!scopedFacts(facts['local:riyadh-dahham'],'ruler',1738).rows.some(r=>r.label==='达哈姆·本·达瓦斯'));
 const context=scopedFacts(facts['local:jomon'],'ruler',-4000).rows;assert.ok(context.length);assert.ok(context.every(r=>r.kind==='unrecorded'));
 for(const[q,y,text]of [['Q33296',1600,'阿克巴'],['Q33296',1857,'巴哈杜尔'],['Q266923',1750,'克里希纳'],['Q2088141',1840,'沙米尔'],['Q2320005',-50,'克娄巴特拉'],['Q180568',-1250,'拉美西斯']])assert.ok(scopedFacts(facts[q],'ruler',y).rows.some(r=>r.label.includes(text)),`${q} ${y}`);
 for(const r of read('public/data/coverage-reigns-review.json').records){assert.ok(/^Q\d+$/.test(r.value));assert.ok(r.citation.length>=2);assert.ok(r.from<=r.to);}
});
test('historical war stages, late intervention and an explicit campaign merge are preserved',()=>{
 const db=read('public/data/conflicts.json'),details=read('public/data/war-details.json');
 assert.ok(!warsAtYear(db,details,609).some(w=>w.id==='historic-sui-goguryeo'));assert.ok(warsAtYear(db,details,612).some(w=>w.id==='historic-sui-goguryeo'));
 const adal=y=>warsAtYear(db,details,y).find(w=>w.id==='historic-ethiopian-adal');assert.ok(!participantsAt(adal(1540),1540).some(p=>p.name.includes('葡萄牙')));assert.ok(participantsAt(adal(1541),1541).some(p=>p.name.includes('葡萄牙')));
 const cauc=warsAtYear(db,details,1820);assert.ok(!cauc.some(w=>w.id==='cow-intra-500'));assert.ok(cauc.find(w=>w.id==='historic-caucasian-group').also.some(w=>w.id==='cow-intra-500'));
 const india=warsAtYear(db,details,1857).find(w=>w.id==='cow-extra-347');assert.ok(india.detail.cause&&india.detail.result);assert.ok(warInvolvesPolity(india,'British India',1857));
});
