import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {activePolities} from '../src/temporal.mjs';
import {pointInGeometry} from '../src/history.mjs';
import {scopedFacts,selectFlag} from '../src/archive-rules.mjs';
import {dependenciesAt} from '../src/relationships.mjs';
import {warsAtYear,participantsAt} from '../src/conflicts.mjs';
import {warInvolvesPolity} from '../src/historical-wars.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const cache=new Map();
const world=y=>{const c=Math.floor(y/100);if(!cache.has(c))cache.set(c,read(`public/data/temporal/${c}.geojson`));return activePolities(cache.get(c),y);};
const owners=(y,p)=>world(y).features.filter(f=>pointInGeometry(p,f.geometry)).map(f=>f.properties.NAME);
const facts=read('public/data/polity-facts.json').entities;
test('Prussia uses real named kings throughout 1701–1918',()=>{
 const people=new Set();for(let y=1701;y<=1918;y++){const r=scopedFacts(facts.Q27306,'ruler',y).rows;assert.ok(r.length,y);assert.ok(r.every(r=>r.value!=='Q3240735'&&r.label!=='普鲁士国王'));r.forEach(r=>people.add(r.value));}assert.equal(people.size,9);
});
test('Xinjiang phases distinguish Qing, Yettishar, Ili and Russian occupation',()=>{
 for(const [y,p,n]of [[1870,[87.6,43.8],'Yettishar'],[1870,[76,39.5],'Yettishar'],[1870,[81.3,43.9],'Ili Sultanate'],[1870,[93.5,42.8],'Qing Dynasty'],[1871,[81.3,43.9],'Russian Empire'],[1877,[87.6,43.8],'Qing Dynasty']])assert.deepEqual(owners(y,p),[n],`${y} ${p}`);
 assert.ok(scopedFacts(facts['local:yettishar'],'ruler',1870).rows.length);
});
test('Libya, Ethiopian restoration and former Ottoman administrations have distinct owners',()=>{
 for(const[y,p,n]of [[1944,[13.2,32.9],'British Tripolitania'],[1944,[20.1,32.1],'British Cyrenaica'],[1944,[14.4,27],'French Fezzan'],[1941,[38.8,9],'Ethiopia'],[1941,[38.9,15.3],'British Administration of Eritrea'],[1918,[44.4,33.3],'British Administration of Mesopotamia'],[1919,[36.3,33.5],'OETA East Arab Administration'],[1919,[35.5,33.9],'OETA Western Military Administration']])assert.deepEqual(owners(y,p),[n],`${y} ${p}`);
});
test('Ceylon 1506 separates Kotte and Kandy and never inherits a British colonial flag',()=>{
 assert.deepEqual(owners(1506,[79.9,6.9]),['Kingdom of Kotte']);assert.deepEqual(owners(1506,[80.64,7.3]),['Kingdom of Kandy']);
 const flags=read('public/data/flags.json').entities;const f=selectFlag(flags['local:kingdom-of-kotte'],1506).flag;assert.ok(f.file.includes('Kotte'));assert.ok(!/Ceylon|British/.test(f.file));assert.ok(scopedFacts(facts['local:kingdom-of-kotte'],'ruler',1506).rows.length);assert.ok(scopedFacts(facts['local:kingdom-of-kandy'],'ruler',1506).rows.length);
});
test('Iran and the East Indies have their correct geography in every affected year',()=>{
 for(let y=1895;y<=1897;y++){assert.deepEqual(owners(y,[51.4,35.7]),['Qajar Dynasty']);assert.deepEqual(owners(y,[106.8,-6.2]),['Dutch East Indies']);}
});
test('Livonian identity is a confederation and Saxon duchies have an imperial superior',()=>{
 const w=world(1444),f=w.features.find(f=>f.properties.NAME==='Livonian Confederation');assert.equal(f?.properties.qid,'Q1064825');assert.ok(!w.features.some(f=>f.properties.qid==='Q33698'));
 const r=dependenciesAt(w,[],1444,read('public/data/curated-facts.json').relations);assert.ok(r.some(r=>r.child==='Ascanian Saxon Duchies'&&r.parent==='Holy Roman Empire'&&r.kind==='vassal'));
 const north=dependenciesAt(world(1750),[],1750,read('public/data/curated-facts.json').relations);assert.ok(north.some(r=>r.parent==='Ottoman Empire'&&/Algiers|Tunis|Tripoli|Karamanli/i.test(r.child)));
});
test('early wars cover BCE and multiple regions while separate invasions retain their gaps',()=>{
 const db=read('public/data/conflicts.json'),details=read('public/data/war-details.json');
 for(const [y,id,country]of [[-218,'historic-punic-second','Roman Republic'],[-261,'historic-kalinga','Maurya Empire'],[627,'historic-byzantine-sasanian','Sasanian Empire'],[1230,'historic-mongol-jin','Mongol Empire'],[1591,'historic-songhai-invasion','Songhai Empire']]){const w=warsAtYear(db,details,y).find(w=>w.id===id);assert.ok(w,id);assert.ok(participantsAt(w,y).some(p=>p.side==='1')&&participantsAt(w,y).some(p=>p.side==='2'));assert.ok(w.detail.cause&&w.detail.result&&w.detail.sources.length);assert.ok(warInvolvesPolity(w,country,y));}
 assert.ok(!warsAtYear(db,details,1276).some(w=>w.id==='historic-mongol-japan'));assert.ok(warsAtYear(db,details,1281).some(w=>w.id==='historic-mongol-japan'));
 for(const[q,y]of [['Q62943',-250],['Q11774',350],['Q6806806',1000],['Q83891',550],['Q184536',1324],['Q2608489',1444]])assert.ok(scopedFacts(facts[q],'ruler',y).rows.length,`${q} ${y}`);
});
